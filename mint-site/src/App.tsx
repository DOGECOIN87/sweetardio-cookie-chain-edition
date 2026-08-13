import { useEffect, useMemo, useState } from 'react'
import { useConnection, useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults'
import { walletAdapterIdentity } from '@metaplex-foundation/umi-signer-wallet-adapters'
import {
  fetchCandyGuard,
  fetchCandyMachine,
  mintV2,
  mplCandyMachine,
} from '@metaplex-foundation/mpl-candy-machine'
import {
  generateSigner,
  isSome,
  publicKey,
  some,
  transactionBuilder,
} from '@metaplex-foundation/umi'
import { base58 } from '@metaplex-foundation/umi/serializers'
import { setComputeUnitLimit } from '@metaplex-foundation/mpl-toolbox'
import { config } from './config'

type DropState = {
  loaded: boolean
  itemsLoaded: number
  itemsRedeemed: number
  priceCook: number | null
  treasury: string
  error?: string
}

const LAMPORTS_PER_COOK = 1_000_000_000

function shortAddress(value: string) {
  return value.length > 12 ? `${value.slice(0, 5)}…${value.slice(-5)}` : value
}

function App() {
  const wallet = useWallet()
  const { connection } = useConnection()
  const [qty, setQty] = useState(1)
  const [balance, setBalance] = useState<number | null>(null)
  const [drop, setDrop] = useState<DropState>({
    loaded: false,
    itemsLoaded: config.totalSupply,
    itemsRedeemed: 0,
    priceCook: null,
    treasury: '',
  })
  const [minting, setMinting] = useState(false)
  const [lastSignature, setLastSignature] = useState('')
  const [notice, setNotice] = useState('')

  const candyMachineConfigured = Boolean(config.candyMachine)
  const treasuryConfigured = Boolean(config.treasury)

  const umi = useMemo(() => {
    const instance = createUmi(config.rpc).use(mplCandyMachine())
    if (wallet.wallet?.adapter) {
      instance.use(walletAdapterIdentity(wallet.wallet.adapter))
    }
    return instance
  }, [wallet.wallet?.adapter, wallet.publicKey?.toBase58()])

  useEffect(() => {
    if (!wallet.publicKey) {
      setBalance(null)
      return
    }
    connection.getBalance(wallet.publicKey)
      .then(lamports => setBalance(lamports / 1_000_000_000))
      .catch(() => setBalance(null))
  }, [connection, wallet.publicKey])

  useEffect(() => {
    let cancelled = false
    async function loadDrop() {
      if (!candyMachineConfigured) {
        setDrop({
          loaded: false,
          itemsLoaded: config.totalSupply,
          itemsRedeemed: 0,
          priceCook: null,
          treasury: '',
          error: 'Candy Machine address has not been deployed/configured yet.',
        })
        return
      }

      try {
        const account = await fetchCandyMachine(umi, publicKey(config.candyMachine))
        const guard = await fetchCandyGuard(umi, account.mintAuthority)
        if (!isSome(guard.guards.solPayment)) {
          throw new Error('Candy Guard does not have a native COOK payment guard.')
        }
        const payment = guard.guards.solPayment.value
        if (cancelled) return
        setDrop({
          loaded: true,
          itemsLoaded: Number(account.data.itemsAvailable),
          itemsRedeemed: Number(account.itemsRedeemed),
          priceCook: Number(payment.lamports.basisPoints) / LAMPORTS_PER_COOK,
          treasury: payment.destination,
        })
      } catch (error) {
        if (cancelled) return
        setDrop({
          loaded: false,
          itemsLoaded: config.totalSupply,
          itemsRedeemed: 0,
          priceCook: null,
          treasury: '',
          error: error instanceof Error ? error.message : 'Unable to load Candy Machine.',
        })
      }
    }
    loadDrop()
    const id = window.setInterval(loadDrop, 15_000)
    return () => { cancelled = true; window.clearInterval(id) }
  }, [umi, candyMachineConfigured])

  const supply = drop.itemsLoaded || config.totalSupply
  const minted = drop.itemsRedeemed
  const progress = Math.min(100, supply ? (minted / supply) * 100 : 0)
  const soldOut = minted >= supply
  const displayedPrice = drop.priceCook ?? config.displayPriceCook
  const treasuryMatches = drop.treasury === config.treasury
  const mintReady = drop.loaded && candyMachineConfigured && treasuryConfigured && treasuryMatches && !soldOut

  async function mintSelected() {
    if (!wallet.connected || !wallet.publicKey || !wallet.wallet?.adapter) {
      setNotice('Connect a Cookie Chain-compatible wallet first.')
      return
    }
    if (!mintReady) {
      if (soldOut) {
        setNotice('Sold out — all 444 Sweetardios have been redeemed.')
        return
      }
      setNotice('Mint is not live: Candy Machine and treasury deployment values are still required.')
      return
    }

    setMinting(true)
    setNotice('')
    try {
      for (let index = 0; index < qty; index += 1) {
        setNotice(`Approve mint ${index + 1} of ${qty} in your wallet…`)
        const candyMachine = await fetchCandyMachine(umi, publicKey(config.candyMachine))
        const guard = await fetchCandyGuard(umi, candyMachine.mintAuthority)
        if (!isSome(guard.guards.solPayment)) {
          throw new Error('Native COOK payment guard is not enabled.')
        }
        if (guard.guards.solPayment.value.destination !== publicKey(config.treasury)) {
          throw new Error('Configured treasury does not match the Candy Guard destination.')
        }
        const nftMint = generateSigner(umi)
        const result = await transactionBuilder()
          .add(setComputeUnitLimit(umi, { units: 800_000 }))
          .add(mintV2(umi, {
            candyMachine: candyMachine.publicKey,
            candyGuard: guard.publicKey,
            nftMint,
            collectionMint: candyMachine.collectionMint,
            collectionUpdateAuthority: candyMachine.authority,
            tokenStandard: candyMachine.tokenStandard,
            mintArgs: {
              solPayment: some({ destination: guard.guards.solPayment.value.destination }),
            },
          }))
          .sendAndConfirm(umi, { confirm: { commitment: 'confirmed' } })
        setLastSignature(base58.deserialize(result.signature)[0])
      }

      setNotice(`${qty} mint${qty === 1 ? '' : 's'} confirmed. Refreshing collection state…`)
      const refreshed = await fetchCandyMachine(umi, publicKey(config.candyMachine))
      setDrop({
        loaded: true,
        itemsLoaded: Number(refreshed.data.itemsAvailable),
        itemsRedeemed: Number(refreshed.itemsRedeemed),
        priceCook: drop.priceCook,
        treasury: drop.treasury,
      })
    } catch (error) {
      console.error(error)
      setNotice(error instanceof Error ? error.message : 'Mint failed.')
    } finally {
      setMinting(false)
    }
  }

  return (
    <div className="site-shell">
      <header>
        <div className="nav wrap">
          <a className="brand" href="#top">
            <strong>SWEETARDIO</strong>
            <span>COOKIE CHAIN EDITION</span>
          </a>
          <nav>
            <a href="#top">HOME</a>
            <a className="active" href="#mint">MINT</a>
            <a href="#collection">COLLECTION</a>
            <a href="#about">ABOUT</a>
          </nav>
          <div className="nav-actions">
            <span className="network-pill"><i /> Cookie Chain</span>
            <WalletMultiButton />
          </div>
        </div>
      </header>

      <main id="top" className="wrap">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">🍪 COOKIE CHAIN</span>
            <h1>SWEETARDIO <em>COOKIE CHAIN</em> <b>EDITION</b></h1>
            <p>
              A curated 444-piece Sweetardio side collection, baked specifically
              for Cookie Chain and powered by the network's native COOK.
            </p>
            <ul>
              <li><span>🍪</span><div><strong>Built for Cookie Chain</strong><small>Native SVM mint, settled in COOK.</small></div></li>
              <li><span>💎</span><div><strong>444 Limited Pieces</strong><small>One compact side edition. No endless supply.</small></div></li>
              <li><span>💙</span><div><strong>Sweetardio DNA</strong><small>The neon collection identity, remixed for Cookie Chain.</small></div></li>
            </ul>
          </div>

          <div className="art-card">
            <span className="serial">444 UNIQUE DRAWS</span>
            <img src="/sample_sheet.png" alt="Selection of Sweetardio Cookie Chain Edition collection art" />
            <div className="art-label"><strong>THE COOKIE CREW</strong><span>ACTUAL COLLECTION SAMPLE</span></div>
          </div>
        </section>

        <section id="collection" className="stats">
          <article><span>TOTAL SUPPLY</span><strong>{supply}</strong><small>Sweetardios</small></article>
          <article>
            <span>MINTED</span><strong>{minted} <small>({progress.toFixed(1)}%)</small></strong>
            <div className="bar"><i style={{ width: `${progress}%` }} /></div>
          </article>
          <article><span>PRICE</span><strong>{displayedPrice} COOK</strong><small>{drop.loaded ? 'Read from Candy Guard' : 'Deployment target'}</small></article>
          <article><span>NETWORK</span><strong className="network-name">🍪 Cookie Chain</strong><small className={drop.error && candyMachineConfigured ? 'offline' : 'live'}>● {drop.error && candyMachineConfigured ? 'RPC ERROR' : 'LIVE'}</small></article>
        </section>

        <section id="mint" className="mint-layout">
          <article className="panel mint-panel">
            <h2>🍪 MINT YOUR SWEETARDIO</h2>
            <div className="mint-controls">
              <div>
                <label>Quantity</label>
                <div className="qty">
                  <button onClick={() => setQty(v => Math.max(1, v - 1))}>−</button>
                  <strong>{qty}</strong>
                  <button onClick={() => setQty(v => Math.min(config.maxPerTx, v + 1))}>+</button>
                </div>
                <small>Max: {config.maxPerTx} per session</small>
              </div>
              <div>
                <label>You will pay</label>
                <div className="price-card">🍪 <strong>{qty * displayedPrice} COOK</strong></div>
              </div>
            </div>

            {!wallet.connected ? (
              <WalletMultiButton className="wide-wallet" />
            ) : (
              <button className="mint-button" disabled={minting || !mintReady} onClick={mintSelected}>
                {soldOut ? 'SOLD OUT' : minting ? 'MINTING…' : `MINT ${qty} SWEETARDIO${qty > 1 ? 'S' : ''}`}
              </button>
            )}

            {notice && <p className="notice">{notice}</p>}
            {!candyMachineConfigured && <p className="setup-warning">Deployment mode: set VITE_CANDY_MACHINE after creating the 444-item Candy Machine.</p>}
            {candyMachineConfigured && !treasuryConfigured && <p className="setup-warning">Deployment mode: set VITE_TREASURY to the Candy Guard payment destination.</p>}
            {drop.loaded && treasuryConfigured && !treasuryMatches && <p className="error-notice">Safety lock: VITE_TREASURY does not match the on-chain Candy Guard.</p>}
            {drop.error && candyMachineConfigured && <p className="error-notice">RPC error: {drop.error}</p>}
            {lastSignature && <a className="tx-link" href={`${config.explorer}/tx/${lastSignature}`} target="_blank" rel="noreferrer">View latest transaction on Cookiescan ↗</a>}
          </article>

          <aside className="sidebar">
            <article className="panel mini">
              <h3>YOUR WALLET</h3>
              <strong>{wallet.publicKey ? shortAddress(wallet.publicKey.toBase58()) : 'Not connected'}</strong>
              <small>{wallet.connected ? 'Connected to mint interface' : 'Connect to check your balance'}</small>
            </article>
            <article className="panel mini">
              <h3>COOKIE BALANCE</h3>
              <strong>{balance == null ? '— COOK' : `${balance.toFixed(4)} COOK`}</strong>
              <small>Native network balance</small>
            </article>
            <article className="panel mini">
              <h3>NETWORK STATUS</h3>
              <strong className="live">● Cookie Chain</strong>
              <small>RPC: {config.rpc}</small>
              <a href={config.explorer} target="_blank" rel="noreferrer">View on Cookiescan ↗</a>
            </article>
          </aside>
        </section>

        <section id="about" className="info-grid">
          <article className="panel"><h3>🍪 ABOUT COOKIE CHAIN</h3><p>An independent SVM network compatible with standard Solana tooling and wallets.</p></article>
          <article className="panel"><h3>🛡 VERIFY COLLECTION</h3><p>{config.candyMachine ? shortAddress(config.candyMachine) : 'Candy Machine address appears here after deployment.'}</p></article>
          <article className="panel"><h3>✨ HOW TO MINT</h3><p>Connect wallet → choose quantity → approve each mint → verify it on Cookiescan.</p></article>
          <article className="panel"><h3>⚙ DEPLOYMENT</h3><p>The UI refuses live minting until the Candy Machine and treasury addresses are configured.</p></article>
        </section>
      </main>

      <footer>
        <div className="wrap footer-inner">
          <div className="brand"><strong>SWEETARDIO</strong><span>COOKIE CHAIN EDITION</span></div>
          <span>444-piece side collection · Cookie Chain</span>
        </div>
      </footer>
    </div>
  )
}

export default App
