(() => {
  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
  const state = document.querySelector("#market-state");
  fetch("/market-data", { headers: { "X-Demo-Confirm": "true" } })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(({ assets }) => {
      assets.forEach((asset) => {
        const row = document.querySelector(
          `[data-market-row="${asset.symbol}"]`,
        );
        if (!row) return;
        row.querySelector("[data-price]").textContent = money.format(
          Number(asset.price),
        );
        const change = Number(asset.change_percent_24h);
        const pill = row.querySelector("[data-change]");
        pill.textContent = `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;
        pill.classList.toggle("up", change >= 0);
        pill.classList.toggle("down", change < 0);
        if (asset.market_cap) {
          row.querySelector("[data-cap]").textContent = money
            .format(Number(asset.market_cap))
            .replace(".00", "");
        }
      });
      const coinGecko = assets.some((asset) => asset.source === "coingecko");
      state.innerHTML = coinGecko
        ? 'Datos actualizados · <a href="https://www.coingecko.com/" target="_blank" rel="noopener">Powered by CoinGecko API</a>'
        : "Datos de mercado actualizados · fuente pública";
    })
    .catch(() => {
      state.textContent =
        "Última referencia disponible · actualización temporalmente no disponible";
    });
})();
