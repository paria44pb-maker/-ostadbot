import axios from "axios";

const API_KEY = process.env.NOBITEX_API_KEY;

const api = axios.create({
  baseURL: "https://api.nobitex.ir",
  headers: {
    Authorization: `Token ${API_KEY}`,
    "Content-Type": "application/json"
  },
  timeout: 20000
});

async function test() {

  try {

    const stats = await api.get("/market/stats");

    console.log(stats.data);

  } catch (err) {

    console.error(
      err.response?.data || err.message
    );
  }
}

test();
