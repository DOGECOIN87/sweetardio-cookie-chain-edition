# Cookie Chain Edition — Developer Deployment Guide

This guide turns the repository’s validated **444-piece Cookie Chain Edition** release into a live **Cookie Chain** mint. Follow the steps in order. The frontend is built for the **Token Metadata Candy Machine v3 + Candy Guard** programs already deployed on Cookie Chain; use the legacy Sugar workflow below rather than the newer `mplx cm create --wizard` Core Candy Machine workflow unless the frontend is also migrated to Core.

> **Never place a seed phrase or private key in this repository, a `.env` file, GitHub, chat, or the hosted website.** The authority keypair stays on the developer’s local machine and signs the collection deployment there.

## 1. What You Need

| Requirement | Why it is needed |
| --- | --- |
| Node.js 22+ and Python 3 | Run the React mint page and recreate the collection. |
| Solana CLI plus a local deployment keypair | Cookie Chain is SVM-compatible and the authority must sign locally. |
| Sugar CLI | Deploys the Token Metadata Candy Machine v3 that the existing frontend reads. |
| Native cCOOK in the authority wallet | Pays Cookie Chain transaction fees, storage, rent, and deploy costs. |
| A public treasury address | Receives the native-COOK mint payments through Candy Guard. |
| A production website domain | Optional for the collection’s external URL, but recommended before public launch. |

Cookie Chain’s canonical RPC is `https://rpc.cookiescan.io`; native **cCOOK** uses 9 decimals and pays fees. The chain includes the Metaplex Candy Machine v3 and Candy Guard programs used by this frontend.[1] [2]

## 2. Set Up the Local Authority

Install the Solana CLI and Sugar on the machine that holds the **deployment authority** keypair. Configure the CLI to Cookie Chain and confirm the address and balance before spending anything.

```bash
solana config set --url https://rpc.cookiescan.io --keypair ~/.config/solana/id.json
solana address
solana balance

# Install the legacy Candy Machine v3 CLI that matches mint-site/src/App.tsx.
bash <(curl -sSf https://raw.githubusercontent.com/metaplex-foundation/sugar/main/script/sugar-install.sh)
sugar --version
```

Use a separate funded authority wallet for the launch. The wallet needs enough cCOOK for storage uploads, account rent, Candy Machine/Candy Guard creation, and a small number of test transactions. Do not use an unfunded wallet or a browser wallet with an unknown network selected.

## 3. Recreate the Final 444-Piece Release

The authoritative release uses seed `871003`, 22 Cookie Chain backgrounds, the Cookboy Handheld as the only arm trait, and Morsel/Cookiebox as sticker-only traits. It must produce exactly **4 Mythic Chase**, **18 Legendary Chase**, **66 Rare**, **134 Uncommon**, and **222 Core** tokens.

```bash
cd sweetardio-cookie-chain-edition
python3 asset_assessment/build_side_collection.py \
  --count 444 \
  --seed 871003 \
  --candidates-per-sticker 120 \
  --workers 4 \
  --out ../cookie-chain-edition-444
```

Before any upload, inspect `../cookie-chain-edition-444/RARITY.md`, `VALIDATION.json`, and the contact sheet. The validation report must confirm 444 images, 444 metadata records, 444 unique public trait signatures, no **Cookie Hands** arm, **Cookboy** as the emboss-background name, and the expected Morsel/Cookiebox sticker counts.

## 4. Create a Sugar-Compatible Asset Folder

Sugar expects local image/JSON pairs indexed from `0`, whereas this repository’s immutable release is numbered from `001`. The helper below preserves the public attributes while creating a deploy-only asset folder.

```bash
python3 asset_assessment/prepare_candy_machine_assets.py \
  --source ../cookie-chain-edition-444 \
  --out ../cookie-chain-candy-machine/assets \
  --count 444

ls ../cookie-chain-candy-machine/assets | head
# Expected: collection.png, collection.json, 0.png, 0.json, 1.png, 1.json, ...
```

Review `collection.png` and `collection.json` before upload. The helper uses token `#001` only as an initial collection image; replace that pair with separately approved collection artwork if required. Do not edit numbered token metadata after the full collection validation unless you recreate and validate the release again.

## 5. Deploy the Candy Machine and Guard

From the Candy Machine staging directory, run Sugar’s interactive launch. Sugar creates the collection NFT, uploads assets, creates the Candy Machine, and maintains a local cache for resumable uploads.[3]

```bash
cd ../cookie-chain-candy-machine
sugar launch --rpc-url https://rpc.cookiescan.io
```

Configure the launch for **444 Token Metadata NFTs**, non-sequential minting, and the intended creator royalty split. Save the generated `config.json` and `cache.json` outside version control.

Then add the native-payment guard. Use the exact payment destination that the collection team has approved; never substitute an address from an explorer search result.

```json
{
  "guards": {
    "default": {
      "solPayment": {
        "value": 10,
        "destination": "<APPROVED_COOKIE_CHAIN_TREASURY_ADDRESS>"
      },
      "mintLimit": {
        "id": 1,
        "limit": 10
      }
    }
  }
}
```

Merge the guard values into the Sugar-generated `config.json`, then apply and inspect them.

```bash
sugar guard add --rpc-url https://rpc.cookiescan.io
sugar show --rpc-url https://rpc.cookiescan.io
sugar guard show --rpc-url https://rpc.cookiescan.io
```

Record the **Candy Machine address** from the Sugar output/cache and the exact `solPayment.destination` from `sugar guard show`. Confirm both accounts on [CookieScan](https://cookiescan.io/) before continuing. The frontend refuses to mint if its configured treasury differs from the on-chain Candy Guard destination.

## 6. Configure and Build the Mint Page

The following values are public deployment configuration, not secrets. Put them in `mint-site/.env` locally and in the production host’s public build environment.

```bash
cd ../sweetardio-cookie-chain-edition/mint-site
cp .env.example .env
```

```env
VITE_COOKIE_RPC=https://rpc.cookiescan.io
VITE_COOKIE_EXPLORER=https://cookiescan.io
VITE_CANDY_MACHINE=<CANDY_MACHINE_FROM_SUGAR>
VITE_TREASURY=<EXACT_SOL_PAYMENT_DESTINATION_FROM_GUARD>
VITE_MINT_PRICE_COOK=10
VITE_MAX_PER_TX=10
```

Build and run the site locally.

```bash
npm install
npm run build
npm run dev -- --host 0.0.0.0 --port 5173
```

Use a Solana-compatible wallet configured to the Cookie Chain custom RPC. Nightly is the project’s supported adapter and is the Cookie Chain developer documentation’s recommended wallet.[1]

## 7. Launch Checklist

| Check | Expected result |
| --- | --- |
| `sugar show` | 444 items available and the expected collection authority. |
| `sugar guard show` | Native-payment amount and destination match the intended public mint. |
| CookieScan | Candy Machine, Candy Guard, and treasury addresses resolve on Cookie Chain. |
| Mint page | Wallet connects on Cookie Chain; price, supply, and remaining count load from the machine. |
| Treasury safety | Any frontend/on-chain destination mismatch leaves the mint button disabled. |
| Controlled test | A team wallet mints one item, then the receipt and NFT are checked on CookieScan before public announcement. |

The repository intentionally cannot deploy the collection by itself: it does not contain an authority keypair, a real treasury address, or a Candy Machine address. Those values must be created and verified by the authorized collection deployer.

## References

[1]: https://raw.githubusercontent.com/cookiechain/agent-skill/main/SKILL.md "Cookie Chain Developer Skill"
[2]: https://raw.githubusercontent.com/cookiechain/agent-skill/main/reference.md "Cookie Chain Developer Reference"
[3]: https://www.metaplex.com/docs/smart-contracts/candy-machine/guides/create-an-nft-collection-on-solana-with-candy-machine "Metaplex: Create a Token Metadata NFT Collection with Candy Machine"
