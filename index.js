import express from "express";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const app = express();

app.use(express.json());

const PORT = process.env.PORT || 3000;

const API_KEY = process.env.NOBITEX_API_KEY;
const SECRET_KEY = process.env.NOBITEX_SECRET_KEY;

// بررسی متغیرها
if (!API_KEY) {
  console.error("❌ NOBITEX_API_KEY not found");
  process.exit(1);
}

if (!SECRET_KEY) {
  console.warn("⚠️ NOBITEX_SECRET_KEY not found");
}

// Axios Instance
const nobitex = axios.create({
  baseURL: "https://api.nobitex.ir",
  timeout: 15000,
  headers: {
    Authorization: `Token ${API_KEY}`,
    "Content-Type": "application/json"
  }
});

// تست اتصال
async function testConnection() {
  try {
    const response = await nobitex.get("/market/stats");

    console.log("✅ Connected to Nobitex");
    console.log("BTC Price:", response.data.stats["btc-usdt"].latest);

  } catch (error) {

    if (error.response) {
      console.error("❌ API Error:");
      console.error(error.response.status);
      console.error(error.response.data);

    } else if (error.request) {
      console.error("❌ No response from Nobitex");

    } else {
      console.error("❌ Error:", error.message);
    }
  }
}

// گرفتن موجودی حساب
app.get("/wallet", async (req, res) => {
  try {

    const response = await nobitex.post("/users/wallets/list");

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {

    res.status(500).json({
      success: false,
      error: error.response?.data || error.message
    });
  }
});

// قیمت لحظه‌ای
app.get("/price/:symbol", async (req, res) => {

  try {

    const symbol = req.params.symbol.toLowerCase();

    const response = await nobitex.get("/market/stats");

    const market = response.data.stats[`${symbol}-usdt`];

    if (!market) {
      return res.status(404).json({
        success: false,
        message: "Symbol not found"
      });
    }

    res.json({
      success: true,
      symbol,
      price: market.latest
    });

  } catch (error) {

    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health Check برای Railway
app.get("/", (req, res) => {
  res.json({
    status: "online",
    exchange: "Nobitex",
    server: "Railway"
  });
});

app.listen(PORT, async () => {

  console.log(`🚀 Server running on port ${PORT}`);

  await testConnection();
});
