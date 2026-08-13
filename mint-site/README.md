# Sweetardio — Cookie Chain Edition Mint

Deploy-ready Vite/React mint frontend for the 444-piece Cookie Chain side edition.

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

Use a local Solana keypair and point the CLI to Cookie Chain:

```bash
solana config set --url https://rpc.cookiescan.io
solana address
solana balance
```

The current Metaplex CLI supports a Candy Machine wizard:

```bash
npm install -g @metaplex-foundation/cli
mplx cm create --wizard
```

Run the wizard on the machine that holds your deployment wallet. Configure a 444-item Candy Machine and a native-payment guard. On Cookie Chain, the SVM native unit is COOK, so the standard native/SOL-payment guard path settles in COOK.

After deployment, copy the resulting Candy Machine and treasury addresses into the frontend environment variables and rebuild.

## Important

This package does not contain a private key and cannot deploy the Candy Machine by itself. The chain deployment must be signed locally by the collection authority wallet.
