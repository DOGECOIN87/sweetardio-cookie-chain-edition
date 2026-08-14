# CookieScan Live Mint Review

CookieScan confirms that Cookie Chain is a live SVM network with the canonical HTTP RPC at `https://rpc.cookiescan.io`, the explorer at `https://cookiescan.io`, native 9-decimal **COOK** fees, and a live transaction stream. The official Cookie Chain developer reference confirms that the chain is Solana-compatible and includes Metaplex **Candy Machine v3** (`CndyV3LdqHUfDLmE5naZjVN8rBZz4tqhdefbAnjHG3JR`) plus **Candy Guard** (`Guard1JwRhJkVH6XZhzoYxeBVQe872VH6QggF4BWmS9g`) as genesis programs.

The existing mint page already targets the correct Cookie Chain RPC, uses the recommended Nightly wallet adapter, and employs Candy Machine v3 / Candy Guard read and mint paths. However, its `VITE_CANDY_MACHINE` and `VITE_TREASURY` values are blank. Without an actual deployed Candy Machine public key and its on-chain payment destination, activating mint transactions would be unsafe and is intentionally prevented.

The CookieScan text search for “Sweetardio” did not expose a collection record or a Candy Machine address. A verified address must therefore be supplied by the collection deployer or obtained from an official collection announcement; it must not be guessed from unrelated explorer data.

| Verified item | Value / conclusion |
| --- | --- |
| Network RPC | `https://rpc.cookiescan.io` |
| Explorer | `https://cookiescan.io` |
| Wallet pattern | Solana-compatible wallet on a custom Cookie Chain RPC; Nightly is the official recommendation. |
| Payment asset | Native cCOOK, 9 decimals. |
| Mint primitives | Candy Machine v3 and Candy Guard are available on Cookie Chain. |
| Current blocker | No verified Cookie Chain Candy Machine public key or payment-destination treasury is present in the repository or publicly discoverable by collection name. |
