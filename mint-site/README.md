# Sweetardio — Cookie Chain Edition Mint

Deploy-ready Vite/React mint frontend for the 444-piece Cookie Chain side edition.

For the complete collection-recreation, Candy Machine v3 deployment, guard,
frontend configuration, and verification process, see the repository-level
[`DEPLOYMENT.md`](../DEPLOYMENT.md). The frontend expects a Token Metadata Candy
Machine v3 deployment; do not use a Core Candy Machine unless the frontend is
migrated to the matching SDK.

## Network

- Cookie Chain RPC: `https://rpc.cookiescan.io`
- Explorer: `https://cookiescan.io`
- Native fee/payment unit: COOK
- Candy Machine v3 program: `CndyV3LdqHUfDLmE5naZjVN8rBZz4tqhdefbAnjHG3JR`
- Candy Guard: `Guard1JwRhJkVH6XZhzoYxeBVQe872VH6QggF4BWmS9g`

## Run

```bash
cp .env.example .env
npm install
npm run dev
```

## Go-live values

Set these after the collection is deployed:

```env
VITE_CANDY_MACHINE=<your Candy Machine address>
VITE_TREASURY=<wallet receiving the native COOK mint payments>
VITE_MINT_PRICE_COOK=<same price configured in the Candy Guard>
```

The UI intentionally disables minting until both on-chain addresses exist. Once
configured, it reads the native COOK price and payment destination from the
Candy Guard account. `VITE_MINT_PRICE_COOK` is only a pre-deployment display
fallback; a treasury mismatch safety-locks the mint.

## Safe deployment workflow

Do not paste a seed phrase/private key into a website, `.env`, GitHub, or chat.

This frontend reads a **Token Metadata Candy Machine v3** through
`@metaplex-foundation/mpl-candy-machine`; therefore, use the matching
**Sugar** deployment workflow documented in [`../DEPLOYMENT.md`](../DEPLOYMENT.md).
The newer `mplx cm create --wizard` command creates a Core Candy Machine and
does not match this frontend unless its mint integration is migrated to the
Core SDK.

After deploying the 444-item machine and a native cCOOK payment guard, copy the
verified Candy Machine address and exact guard destination into the frontend
environment variables, then rebuild. The UI safety-locks minting whenever those
values are absent or disagree with the on-chain guard.

## Important

This package does not contain a private key and cannot deploy the Candy Machine by itself. The chain deployment must be signed locally by the collection authority wallet.
