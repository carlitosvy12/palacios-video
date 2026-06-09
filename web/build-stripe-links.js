const fs = require("fs");
const path = require("path");

const links = {
  creator: process.env.STRIPE_LINK_CREATOR || "",
  pro: process.env.STRIPE_LINK_PRO || "",
  agencia: process.env.STRIPE_LINK_AGENCIA || "",
};

const config = {
  stripeLinks: links,
  supabaseUrl: process.env.SUPABASE_URL || "",
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY || "",
};

const output = [
  `window.PALACIOS_STRIPE_LINKS = ${JSON.stringify(links, null, 2)};`,
  `window.PALACIOS_CONFIG = ${JSON.stringify(config, null, 2)};`,
  "",
].join("\n");

fs.writeFileSync(path.join(__dirname, "stripe-links.js"), output, "utf8");
console.log("Stripe payment links generated for static site.");
