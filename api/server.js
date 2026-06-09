import express from "express";
import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";

const {
  PORT = 10000,
  STRIPE_SECRET_KEY,
  STRIPE_WEBHOOK_SECRET,
  SUPABASE_URL,
  SUPABASE_SERVICE_ROLE_KEY,
} = process.env;

const PLAN_LIMITS = {
  creator: 5,
  pro: 20,
  agencia: 80,
};

const stripe = STRIPE_SECRET_KEY ? new Stripe(STRIPE_SECRET_KEY) : null;
const supabase =
  SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY
    ? createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    : null;

const app = express();

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "palacios-video-api" });
});

app.post(
  "/stripe/webhook",
  express.raw({ type: "application/json" }),
  async (req, res) => {
    if (!stripe || !supabase || !STRIPE_WEBHOOK_SECRET) {
      return res.status(500).json({ error: "Webhook environment is not configured." });
    }

    const signature = req.headers["stripe-signature"];
    let event;

    try {
      event = stripe.webhooks.constructEvent(req.body, signature, STRIPE_WEBHOOK_SECRET);
    } catch (error) {
      return res.status(400).send(`Webhook signature error: ${error.message}`);
    }

    try {
      if (event.type === "checkout.session.completed") {
        await handleCheckoutCompleted(event.data.object);
      }

      if (
        event.type === "customer.subscription.updated" ||
        event.type === "customer.subscription.deleted"
      ) {
        await handleSubscriptionChange(event.data.object);
      }
    } catch (error) {
      console.error(error);
      return res.status(500).json({ error: "Webhook handler failed." });
    }

    res.json({ received: true });
  },
);

async function handleCheckoutCompleted(session) {
  const userId = session.client_reference_id;
  const plan = normalizePlan(session.metadata?.plan);

  if (!userId || !plan) {
    console.warn("Missing client_reference_id or metadata.plan in checkout session", {
      sessionId: session.id,
      userId,
      plan: session.metadata?.plan,
    });
    return;
  }

  const subscription =
    typeof session.subscription === "string"
      ? await stripe.subscriptions.retrieve(session.subscription)
      : session.subscription;

  const renovacion = subscription?.current_period_end
    ? new Date(subscription.current_period_end * 1000).toISOString()
    : null;

  await upsertSubscription({
    user_id: userId,
    plan,
    stripe_customer_id: session.customer || null,
    stripe_subscription_id: session.subscription || null,
    estado: subscription?.status || "active",
    horas_limite: PLAN_LIMITS[plan],
    renovacion,
  });
}

async function handleSubscriptionChange(subscription) {
  const { data: existing } = await supabase
    .from("suscripciones")
    .select("user_id, plan")
    .eq("stripe_subscription_id", subscription.id)
    .maybeSingle();

  if (!existing) {
    console.warn("Subscription not found in Supabase", subscription.id);
    return;
  }

  await upsertSubscription({
    user_id: existing.user_id,
    plan: existing.plan,
    stripe_customer_id: subscription.customer || null,
    stripe_subscription_id: subscription.id,
    estado: subscription.status,
    horas_limite: PLAN_LIMITS[existing.plan] || 0,
    renovacion: subscription.current_period_end
      ? new Date(subscription.current_period_end * 1000).toISOString()
      : null,
  });
}

async function upsertSubscription(payload) {
  const { error } = await supabase.from("suscripciones").upsert(
    {
      ...payload,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id" },
  );

  if (error) {
    throw error;
  }
}

function normalizePlan(plan) {
  const value = String(plan || "").toLowerCase();
  return PLAN_LIMITS[value] ? value : null;
}

app.use(express.json());

app.listen(PORT, () => {
  console.log(`Palacios Video API listening on ${PORT}`);
});
