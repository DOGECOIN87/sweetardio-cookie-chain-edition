// Design: Cookie Chain Edition inherits Sweetardio's midnight-blue arcade atmosphere,
// collectible character-card framing, technical mono metadata, and cyan/cerise signal states.
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

const featuredSweetardios = [
  { id: '003', name: 'Chocolate Sandwich Cookie', image: '/featured/chocolate-sandwich.png', background: 'Cookboy Chocolate', traits: ['Smug eyes', 'Sad mouth', 'Cookie Monster slippers'] },
  { id: '021', name: 'Gold Waffle', image: '/featured/gold-waffle.png', background: 'Oxford Blue Fur', traits: ['Clueless eyes', 'Smirk', 'Gold edition'] },
  { id: '026', name: 'Zebra Cake', image: '/featured/zebra-cake.png', background: 'Yatrah Arcade', traits: ['Side-eye', 'Smirk', 'Cookiebox sticker'] },
  { id: '034', name: 'OG Gummy Bear', image: '/featured/og-gummy-bear.png', background: 'Digital Future Mural', traits: ['Smug eyes', 'Smirk', 'Cookboy Handheld'] },
  { id: '042', name: 'Cyan Sherbert Ice Cream', image: '/featured/cyan-sherbert.png', background: 'Midnight Bakery', traits: ['Cerise eyes', 'Smoke mouth', 'Morsel sticker'] },
] as const

const supplyFacts = [
  ['Network', 'Cookie Chain', 'Native SVM mint'],
  ['Edition', '444', 'Finalized unique tokens'],
  ['Traits', 'MORSEL + COOKIEBOX', 'Sticker registry'],
  ['Currency', 'COOK', 'Native settlement'],
] as const

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
  const [featuredIndex, setFeaturedIndex] = useState(0)

  const candyMachineConfigured = Boolean(config.candyMachine)
  const treasuryConfigured = Boolean(config.treasury)

  const umi = useMemo(() => {
    const instance = createUmi(config.rpc).use(mplCandyMachine())
    if (wallet.wallet?.adapter) instance.use(walletAdapterIdentity(wallet.wallet.adapter))
    return instance
  }, [wallet.wallet?.adapter, wallet.publicKey?.toBase58()])

  useEffect(() => {
    if (!wallet.publicKey) {
      setBalance(null)
      return
    }
    connection.getBalance(wallet.publicKey)
      .then(lamports => setBalance(lamports / LAMPORTS_PER_COOK))
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
        if (!isSome(guard.guards.solPayment)) throw new Error('Candy Guard does not have a native COOK payment guard.')
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
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [umi, candyMachineConfigured])

  const supply = drop.itemsLoaded || config.totalSupply
  const minted = drop.itemsRedeemed
  const progress = Math.min(100, supply ? (minted / supply) * 100 : 0)
  const soldOut = minted >= supply
  const displayedPrice = drop.priceCook ?? config.displayPriceCook
  const treasuryMatches = drop.treasury === config.treasury
  const mintReady = drop.loaded && candyMachineConfigured && treasuryConfigured && treasuryMatches && !soldOut
  const featured = featuredSweetardios[featuredIndex]
  const remaining = Math.max(0, supply - minted)

  useEffect(() => {
    const id = window.setInterval(() => {
      setFeaturedIndex(current => (current + 1) % featuredSweetardios.length)
    }, 6500)
    return () => window.clearInterval(id)
  }, [])

  async function mintSelected() {
    if (!wallet.connected || !wallet.publicKey || !wallet.wallet?.adapter) {
      setNotice('Connect a Cookie Chain-compatible wallet first.')
      return
    }
    if (!mintReady) {
      setNotice(soldOut
        ? 'Sold out — all 444 Sweetardios have been redeemed.'
        : 'Mint is not live: Candy Machine and treasury deployment values are still required.')
      return
    }

    setMinting(true)
    setNotice('')
    try {
      for (let index = 0; index < qty; index += 1) {
        setNotice(`Approve mint ${index + 1} of ${qty} in your wallet…`)
        const candyMachine = await fetchCandyMachine(umi, publicKey(config.candyMachine))
        const guard = await fetchCandyGuard(umi, candyMachine.mintAuthority)
        if (!isSome(guard.guards.solPayment)) throw new Error('Native COOK payment guard is not enabled.')
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
            mintArgs: { solPayment: some({ destination: guard.guards.solPayment.value.destination }) },
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

  function focusMint() {
    document.getElementById('mint')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="site-shell" id="top">
      <div className="ambient ambient-one" aria-hidden="true" />
      <div className="ambient ambient-two" aria-hidden="true" />

      <header className="topbar">
        <div className="wrap navigation">
          <a className="brand" href="#top" aria-label="Sweetardio Cookie Chain Edition home">
            <span className="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span>
            <span><strong>SWEETARDIO</strong><small>COOKIE CHAIN EDITION</small></span>
          </a>
          <nav aria-label="Primary navigation">
            <a href="#collection">Collection</a>
            <a href="#mint">Mint</a>
            <a href="#about">Details</a>
          </nav>
          <div className="nav-actions">
            <span className="network-pill"><b /> Cookie Chain</span>
            <WalletMultiButton />
          </div>
        </div>
      </header>

      <main>
        <section className="hero wrap" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="signal-line"><span>DROP // COOKIE.444</span><i /><span>LIVE STATUS</span></div>
            <p className="eyebrow">SWEETARDIO SIDE COLLECTION · FINALIZED 444</p>
            <h1 id="hero-title"><span>THE</span> <em>COOKIE CHAIN</em> <b>EDITION</b></h1>
            <p className="hero-description">Four hundred and forty-four unique Sweetardios, baked for Cookie Chain. Every mint reveals a collectible character card from the finalized official side edition.</p>
            <div className="hero-actions">
              <button className="primary-cta" type="button" onClick={focusMint}>ENTER THE MINT <span>↓</span></button>
              <a className="text-link" href="#collection">VIEW THE EDITION <span>→</span></a>
            </div>
            <dl className="hero-facts">
              {supplyFacts.map(([label, value, detail]) => <div key={label}><dt>{label}</dt><dd>{value}</dd><small>{detail}</small></div>)}
            </dl>
          </div>

          <article className="feature-card" aria-label="Featured Cookie Chain Sweetardio">
            <div className="feature-radar" aria-hidden="true"><span /><span /><span /></div>
            <div className="card-topline"><span>CURATED DRAW</span><b>#{featured.id}</b></div>
            <div className="feature-art">
              <img src={featured.image} alt={`Sweetardio #${featured.id}: ${featured.name}`} />
              <span className="art-corner top-left" aria-hidden="true" /><span className="art-corner top-right" aria-hidden="true" />
              <span className="art-corner bottom-left" aria-hidden="true" /><span className="art-corner bottom-right" aria-hidden="true" />
            </div>
            <div className="feature-caption">
              <div><small>SWEETARDIO #{featured.id}</small><h2>{featured.name}</h2></div>
              <span className="verified">VERIFIED</span>
            </div>
            <div className="feature-traits">
              <span>BG / {featured.background}</span>
              {featured.traits.slice(0, 2).map(trait => <span key={trait}>{trait}</span>)}
            </div>
            <div className="feature-tabs" aria-label={`Featured character ${featuredIndex + 1} of ${featuredSweetardios.length}`}>
              {featuredSweetardios.map((item, index) => <button type="button" className={index === featuredIndex ? 'active' : ''} key={item.id} onClick={() => setFeaturedIndex(index)} aria-label={`Show Sweetardio #${item.id}`} />)}
            </div>
          </article>
        </section>

        <section className="status-band" id="collection" aria-label="Drop status">
          <div className="wrap status-grid">
            <div className="status-title"><span>COOKIESCAN SIGNAL</span><strong><i /> {drop.error && candyMachineConfigured ? 'SYNC INTERRUPTED' : 'NETWORK LIVE'}</strong></div>
            <div className="status-stat"><span>SUPPLY</span><b>{supply}</b><small>SWEETARDIOS</small></div>
            <div className="status-stat"><span>REDEEMED</span><b>{minted}</b><small>{progress.toFixed(1)}% OF DROP</small></div>
            <div className="status-progress"><div><span>EDITION PROGRESS</span><b>{remaining} remaining</b></div><div className="progress-track"><i style={{ width: `${progress}%` }} /></div></div>
          </div>
        </section>

        <section className="mint-zone wrap" id="mint" aria-labelledby="mint-heading">
          <div className="section-marker"><span>01</span><i /><p>COOKIE CHAIN MINT TERMINAL</p></div>
          <div className="mint-layout">
            <article className="mint-terminal">
              <div className="terminal-heading"><div><p>SECURE MINT ROUTE</p><h2 id="mint-heading">Claim your <em>Sweetardio</em></h2></div><span className={mintReady ? 'terminal-state ready' : 'terminal-state'}>{mintReady ? 'READY' : soldOut ? 'SOLD OUT' : 'AWAITING DEPLOYMENT'}</span></div>

              <div className="mint-controls">
                <div className="control-box"><label htmlFor="mint-qty">MINT QUANTITY</label><div className="quantity-control"><button type="button" onClick={() => setQty(value => Math.max(1, value - 1))} aria-label="Decrease mint quantity">−</button><output id="mint-qty">{qty}</output><button type="button" onClick={() => setQty(value => Math.min(config.maxPerTx, value + 1))} aria-label="Increase mint quantity">+</button></div><small>Maximum {config.maxPerTx} per transaction</small></div>
                <div className="control-box cost-box"><label>YOU WILL PAY</label><strong>{qty * displayedPrice} <small>COOK</small></strong><span>{drop.loaded ? 'Price read from Candy Guard' : 'Deployment target price'}</span></div>
              </div>

              <div className="mint-action">
                {!wallet.connected ? <WalletMultiButton className="wide-wallet" /> : <button className="mint-button" disabled={minting || !mintReady} onClick={mintSelected}>{soldOut ? 'EDITION SOLD OUT' : minting ? 'MINTING…' : `MINT ${qty} SWEETARDIO${qty > 1 ? 'S' : ''}`}<span>↗</span></button>}
                <p className="safety-note">Transactions are enabled only when the collection’s configured treasury matches the active Candy Guard.</p>
              </div>

              {notice && <p className="notice" role="status">{notice}</p>}
              {!candyMachineConfigured && <p className="setup-warning">Deployment mode: set <code>VITE_CANDY_MACHINE</code> after creating the 444-item Candy Machine.</p>}
              {candyMachineConfigured && !treasuryConfigured && <p className="setup-warning">Deployment mode: set <code>VITE_TREASURY</code> to the Candy Guard payment destination.</p>}
              {drop.loaded && treasuryConfigured && !treasuryMatches && <p className="error-notice">Safety lock: <code>VITE_TREASURY</code> does not match the on-chain Candy Guard destination.</p>}
              {drop.error && candyMachineConfigured && <p className="error-notice">RPC error: {drop.error}</p>}
              {lastSignature && <a className="tx-link" href={`${config.explorer}/tx/${lastSignature}`} target="_blank" rel="noreferrer">View the latest transaction on Cookiescan <span>↗</span></a>}
            </article>

            <aside className="terminal-sidebar" aria-label="Wallet and drop details">
              <article className="identity-card"><span className="scan-lines" aria-hidden="true" /><p>CONNECTED IDENTITY</p><strong>{wallet.publicKey ? shortAddress(wallet.publicKey.toBase58()) : 'WALLET OFFLINE'}</strong><small>{wallet.connected ? 'Wallet recognized by mint terminal' : 'Connect a compatible wallet to begin'}</small></article>
              <article className="balance-card"><p>COOKIE BALANCE</p><strong>{balance == null ? '—' : balance.toFixed(4)} <em>COOK</em></strong><small>Native network balance</small></article>
              <article className="verify-card"><span>COLLECTION CHECK</span><p>{config.candyMachine ? shortAddress(config.candyMachine) : 'CANDY MACHINE PENDING'}</p><a href={config.explorer} target="_blank" rel="noreferrer">OPEN COOKIESCAN ↗</a></article>
            </aside>
          </div>
        </section>

        <section className="gallery-wrap wrap" aria-labelledby="gallery-heading">
          <div className="section-marker"><span>02</span><i /><p>CURATED DRAW PREVIEW</p></div>
          <div className="gallery-heading"><div><h2 id="gallery-heading">A side edition <em>with main-event energy.</em></h2><p>Each Sweetardio is composed from the edition’s own sharp source backgrounds, character art, and finalized trait registry: the Cookboy Handheld arm plus Morsel and Cookiebox sticker traits.</p></div><span>{featuredSweetardios.length} FEATURED DRAWS</span></div>
          <div className="character-grid">
            {featuredSweetardios.map((item, index) => <button className={index === featuredIndex ? 'character-card selected' : 'character-card'} key={item.id} type="button" onClick={() => setFeaturedIndex(index)}><img src={item.image} alt={`Select Sweetardio #${item.id}: ${item.name}`} /><span className="character-no">#{item.id}</span><span className="character-name">{item.name}</span><i aria-hidden="true">VIEW</i></button>)}
          </div>
        </section>

        <section className="details-section" id="about">
          <div className="wrap details-grid">
            <div className="details-intro"><p className="eyebrow">COOKIE CHAIN / SWEETARDIO</p><h2>Mint small. <em>Collect loud.</em></h2><p>The Cookie Chain Edition is a compact, native-COOK Sweetardio release: 444 character-driven pieces, a guarded mint path, and an edition designed to sit beside the original collection—not apart from it.</p></div>
            <div className="detail-list"><article><span>01</span><div><h3>Native COOK settlement</h3><p>Mint directly on Cookie Chain with the network’s native currency and standard wallet tooling.</p></div></article><article><span>02</span><div><h3>Guarded collection route</h3><p>The mint interface checks the Candy Machine and configured treasury before any live transaction is enabled.</p></div></article><article><span>03</span><div><h3>Finalized trait registry</h3><p>The limited Cookboy Handheld is the edition’s arm trait. Morsel and Cookiebox are sticker traits, composed from the edition’s sharp source-art pipeline.</p></div></article></div>
          </div>
        </section>
      </main>

      <footer><div className="wrap footer-inner"><a className="brand" href="#top"><span className="brand-mark" aria-hidden="true"><i /><i /><i /><i /></span><span><strong>SWEETARDIO</strong><small>COOKIE CHAIN EDITION</small></span></a><p>© SWEETARDIO · 444 PIECE SIDE COLLECTION · COOKIE CHAIN</p><a href="#mint">RETURN TO MINT ↑</a></div></footer>
    </div>
  )
}

export default App
