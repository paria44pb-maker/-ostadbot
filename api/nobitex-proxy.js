import fetch from "node-fetch";

export default async function handler(req, res) {
  const endpoint = req.query.endpoint;

  if (!endpoint) {
    return res.status(400).json({ error: "Endpoint is required" });
  }

  try {
    const response = await fetch(`https://api.nobitex.ir/${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    return res.status(200).json(data);

  } catch (err) {
    return res.status(500).json({
      error: "Proxy Error",
      message: err.message,
    });
  }
}
`
