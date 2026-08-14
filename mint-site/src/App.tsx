// Design: Reference-led Sweetardio.fun neon arcade — Oxford Blue environment, cerise/cyan
// glow, glass arcade panels, aisle dividers, sugar-dust atmosphere, and full-quality token art.
import { useEffect, useMemo, useState } from 'react'
import { useConnection, useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults'
import { walletAdapterIdentity } from '@metaplex-foundation/umi-signer-wallet-adapters'
import { fetchCandyGuard, fetchCandyMachine, mintV2, mplCandyMachine } from '@metaplex-foundation/mpl-candy-machine'
import { generateSigner, isSome, publicKey, some, transactionBuilder } from '@metaplex-foundation/umi'
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
  { id: '003', name: 'Marshmallow', image: '/featured/003.png', background: 'Simplex Arcade', traits: ['Smug eyes', 'Out of Order sticker', 'Rare'] },
  { id: '021', name: 'Cyan Frosted Pop Tart', image: '/featured/021.png', background: 'Yatrah Arcade', traits: ['Cyan eyes', 'Morsel sticker', 'Core'] },
  { id: '013', name: 'Vanilla Ice Cream', image: '/featured/013.png', background: 'Midnight Bakery', traits: ['Cyborg eyes', 'Morsel sticker', 'Uncommon'] },
  { id: '067', name: 'Pink Sherbert Ice Cream', image: '/featured/067.png', background: 'Emyr Gallery', traits: ['Cookboy Handheld', 'Mythic Chase', 'Poptart Cat sticker'] },
  { id: '068', name: 'Waffle', image: '/featured/068.png', background: 'Cookboy', traits: ['Cyborg eyes', 'Shorts Doggo sticker', 'Uncommon'] },
] as const

const DUST = [
  ['7%', '13%', 'cerise'], ['18%', '71%', 'cyan'], ['31%', '23%', 'white'], ['46%', '82%', 'cerise'],
  ['59%', '17%', 'cyan'], ['72%', '62%', 'white'], ['88%', '28%', 'cerise'], ['94%', '75%', 'cyan'],
] as const

function shortAddress(value: string) {
  return value.length > 12 ? `${value.slice(0, 5)}…${value.slice(-5)}` : value
}

function App() {
  const wallet = useWallet()
  const { connection } = useConnection()
  const [qty, setQty] = useState(1)
  const [balance, setBalance] = useState<number | null>(null)
  const [drop, setDrop] = useState<DropState>({ loaded: false, itemsLoaded: config.totalSupply, itemsRedeemed: 0, priceCook: null, treasury: '' })
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
    if (!wallet.publicKey) { setBalance(null); return }
    connection.getBalance(wallet.publicKey).then(lamports => setBalance(lamports / LAMPORTS_PER_COOK)).catch(() => setBalance(null))
  }, [connection, wallet.publicKey])

  useEffect(() => {
    let cancelled = false
    async function loadDrop() {
      if (!candyMachineConfigured) {
        setDrop({ loaded: false, itemsLoaded: config.totalSupply, itemsRedeemed: 0, priceCook: null, treasury: '', error: 'Candy Machine address has not been deployed/configured yet.' })
        return
      }
      try {
        const account = await fetchCandyMachine(umi, publicKey(config.candyMachine))
        const guard = await fetchCandyGuard(umi, account.mintAuthority)
        if (!isSome(guard.guards.solPayment)) throw new Error('Candy Guard does not have a native COOK payment guard.')
        const payment = guard.guards.solPayment.value
        if (!cancelled) setDrop({ loaded: true, itemsLoaded: Number(account.data.itemsAvailable), itemsRedeemed: Number(account.itemsRedeemed), priceCook: Number(payment.lamports.basisPoints) / LAMPORTS_PER_COOK, treasury: payment.destination })
      } catch (error) {
        if (!cancelled) setDrop({ loaded: false, itemsLoaded: config.totalSupply, itemsRedeemed: 0, priceCook: null, treasury: '', error: error instanceof Error ? error.message : 'Unable to load Candy Machine.' })
      }
    }
    loadDrop()
    const id = window.setInterval(loadDrop, 15_000)
    return () => { cancelled = true; window.clearInterval(id) }
  }, [umi, candyMachineConfigured])

  const supply = drop.itemsLoaded || config.totalSupply
  const minted = drop.itemsRedeemed
  const remaining = Math.max(0, supply - minted)
  const progress = Math.min(100, supply ? (minted / supply) * 100 : 0)
  const soldOut = minted >= supply
  const displayedPrice = drop.priceCook ?? config.displayPriceCook
  const treasuryMatches = drop.treasury === config.treasury
  const mintReady = drop.loaded && candyMachineConfigured && treasuryConfigured && treasuryMatches && !soldOut
  const featured = featuredSweetardios[featuredIndex]

  useEffect(() => {
    const id = window.setInterval(() => setFeaturedIndex(current => (current + 1) % featuredSweetardios.length), 6500)
    return () => window.clearInterval(id)
  }, [])

  async function mintSelected() {
    if (!wallet.connected || !wallet.publicKey || !wallet.wallet?.adapter) { setNotice('Connect a Cookie Chain-compatible wallet first.'); return }
    if (!mintReady) { setNotice(soldOut ? 'Sold out — all 444 Sweetardios have been redeemed.' : 'Mint is not live: Candy Machine and treasury deployment values are still required.'); return }
    setMinting(true); setNotice('')
    try {
      for (let index = 0; index < qty; index += 1) {
        setNotice(`Approve mint ${index + 1} of ${qty} in your wallet…`)
        const candyMachine = await fetchCandyMachine(umi, publicKey(config.candyMachine))
        const guard = await fetchCandyGuard(umi, candyMachine.mintAuthority)
        if (!isSome(guard.guards.solPayment)) throw new Error('Native COOK payment guard is not enabled.')
        if (guard.guards.solPayment.value.destination !== publicKey(config.treasury)) throw new Error('Configured treasury does not match the Candy Guard destination.')
        const nftMint = generateSigner(umi)
        const result = await transactionBuilder().add(setComputeUnitLimit(umi, { units: 800_000 })).add(mintV2(umi, {
          candyMachine: candyMachine.publicKey,
          candyGuard: guard.publicKey,
          nftMint,
          collectionMint: candyMachine.collectionMint,
          collectionUpdateAuthority: candyMachine.authority,
          tokenStandard: candyMachine.tokenStandard,
          mintArgs: { solPayment: some({ destination: guard.guards.solPayment.value.destination }) },
        })).sendAndConfirm(umi, { confirm: { commitment: 'confirmed' } })
        setLastSignature(base58.deserialize(result.signature)[0])
      }
      const refreshed = await fetchCandyMachine(umi, publicKey(config.candyMachine))
      setDrop({ loaded: true, itemsLoaded: Number(refreshed.data.itemsAvailable), itemsRedeemed: Number(refreshed.itemsRedeemed), priceCook: drop.priceCook, treasury: drop.treasury })
      setNotice(`${qty} mint${qty === 1 ? '' : 's'} confirmed. Collection state refreshed.`)
    } catch (error) {
      console.error(error)
      setNotice(error instanceof Error ? error.message : 'Mint failed.')
    } finally { setMinting(false) }
  }

  const focusMint = () => document.getElementById('mint')?.scrollIntoView({ behavior: 'smooth', block: 'start' })

  return (
    <div className="arcade-shell" id="top">
      <div className="arcade-background" aria-hidden="true" />
      <div className="arcade-scanlines" aria-hidden="true" />
      <div className="arcade-grain" aria-hidden="true" />
      <div className="sugar-dust" aria-hidden="true">{DUST.map(([left, top, color], index) => <i key={index} className={color} style={{ left, top, animationDelay: `${index * -1.7}s` }} />)}</div>

      <header className="arcade-nav">
        <a className="sweetardio-lockup" href="#top" aria-label="Sweetardio Cookie Chain Edition home"><span><b>SWEET</b><em>ARDIO</em></span><small>COOKIE CHAIN EDITION</small></a>
        <nav aria-label="Primary navigation"><a href="#edition">The Edition</a><a href="#mint">Mint</a><a href="#registry">Traits</a></nav>
        <div className="nav-wallet"><span className="arcade-live"><i /> COOKIE CHAIN</span><WalletMultiButton /></div>
      </header>

      <main>
        <section className="arcade-hero" aria-labelledby="hero-title">
          <div className="hero-vignette" aria-hidden="true" />
          <div className="hero-console">
            <div className="hero-token"><i /> FINALIZED EDITION <span>•</span> 444 UNIQUE MINTS</div>
            <div className="hero-badge hero-badge-logo"><span className="cookie-orbit">✦</span><img src="/cookie-chain-edition-logo.png" alt="Cookie Chain Edition" /></div>
            <p className="hero-kicker">SWEETARDIO PRESENTS</p>
            <h1 id="hero-title"><span><b>SWEET</b><em>ARDIO</em></span><strong>COOKIE CHAIN</strong></h1>
            <p className="hero-copy">A sugar-coated side edition, built from the original Sweetardio collection’s character system and released as <b>444</b> unique Cookie Chain collectibles.</p>
            <p className="hero-direction">FOLLOW THE NEON — WALK UP TO THE MINT</p>
            <div className="hero-cta-row"><button type="button" className="neon-action cyan" onClick={focusMint}>ENTER MINT <span>↑</span></button><a href="#edition" className="neon-action ghost">EXPLORE EDITION <span>→</span></a></div>
          </div>
        </section>

        <section className="ticker-rail" aria-label="Edition highlights"><span>COOKIE CHAIN EDITION</span><i>◆</i><span>444 UNIQUE TOKENS</span><i>◆</i><span>MORSEL + COOKIEBOX STICKERS</span><i>◆</i><span>COOKBOY HANDHELD</span><i>◆</i><span>COOKIE CHAIN EDITION</span></section>

        <section className="arcade-aisle" id="edition"><div><b>01</b><span>THE CURATED WALL</span></div><i /></section>

        <section className="edition-stage wrap">
          <div className="edition-intro"><p className="arcade-label">OFFICIAL SIDE EDITION</p><h2>Every draw is a <em>full-quality</em> character card.</h2><p>Featured previews are direct 1393px renders from the finalized collection — the same sharp source-art pipeline that defines the mint.</p><dl><div><dt>SUPPLY</dt><dd>{supply}</dd></div><div><dt>REMAINING</dt><dd>{remaining}</dd></div><div><dt>STATUS</dt><dd>{mintReady ? 'LIVE' : 'STAGED'}</dd></div></dl></div>
          <article className="arcade-card featured-card" aria-label="Featured Cookie Chain Sweetardio">
            <div className="card-signal"><span>CURATED DRAW</span><b>#{featured.id}</b></div>
            <div className="featured-art"><img src={featured.image} alt={`Sweetardio #${featured.id}: ${featured.name}`} /><span className="finder tl" /><span className="finder tr" /><span className="finder bl" /><span className="finder br" /></div>
            <div className="featured-meta"><div><small>SWEETARDIO #{featured.id}</small><h3>{featured.name}</h3></div><strong>{featured.traits[2]}</strong></div>
            <p className="featured-readout">BG / {featured.background} <span>◆</span> {featured.traits[0]} <span>◆</span> {featured.traits[1]}</p>
            <div className="draw-switcher" aria-label={`Featured character ${featuredIndex + 1} of ${featuredSweetardios.length}`}>{featuredSweetardios.map((item, index) => <button type="button" className={index === featuredIndex ? 'active' : ''} key={item.id} onClick={() => setFeaturedIndex(index)} aria-label={`Show Sweetardio #${item.id}`}>{item.id}</button>)}</div>
          </article>
        </section>

        <section className="arcade-aisle cerise"><div><b>02</b><span>THE MINT COUNTER</span></div><i /></section>

        <section className="mint-bay wrap" id="mint" aria-labelledby="mint-heading">
          <article className="mint-panel arcade-card">
            <div className="panel-head"><div><p className="arcade-label">COOKIE CHAIN MINT</p><h2 id="mint-heading">Walk up. <em>Pick your draw.</em></h2></div><span className={mintReady ? 'mint-state live' : 'mint-state'}>{mintReady ? 'MINT LIVE' : soldOut ? 'SOLD OUT' : 'AWAITING DEPLOYMENT'}</span></div>
            <div className="mint-grid">
              <div className="mint-control"><label htmlFor="mint-qty">HOW MANY?</label><div className="quantity-control"><button type="button" onClick={() => setQty(value => Math.max(1, value - 1))} aria-label="Decrease mint quantity">−</button><output id="mint-qty">{qty}</output><button type="button" onClick={() => setQty(value => Math.min(config.maxPerTx, value + 1))} aria-label="Increase mint quantity">+</button></div><small>UP TO {config.maxPerTx} PER WALK-UP</small></div>
              <div className="mint-control price"><label>COUNTER TOTAL</label><strong>{qty * displayedPrice} <em>COOK</em></strong><small>{drop.loaded ? 'CANDY GUARD PRICE' : 'TARGET MINT PRICE'}</small></div>
            </div>
            <div className="mint-action">{!wallet.connected ? <WalletMultiButton className="wide-wallet" /> : <button className="neon-action cyan mint-submit" disabled={minting || !mintReady} onClick={mintSelected}>{soldOut ? 'EDITION SOLD OUT' : minting ? 'MINTING…' : `MINT ${qty} SWEETARDIO${qty > 1 ? 'S' : ''}`} <span>↗</span></button>}<p>Transactions enable only when the active Candy Guard and configured treasury agree.</p></div>
            {notice && <p className="terminal-notice" role="status">{notice}</p>}
            {!candyMachineConfigured && <p className="terminal-warning">Deployment mode: set <code>VITE_CANDY_MACHINE</code> after creating the 444-item Candy Machine.</p>}
            {candyMachineConfigured && !treasuryConfigured && <p className="terminal-warning">Deployment mode: set <code>VITE_TREASURY</code> to the Candy Guard payment destination.</p>}
            {drop.loaded && treasuryConfigured && !treasuryMatches && <p className="terminal-error">Safety lock: configured treasury differs from the on-chain Candy Guard destination.</p>}
            {drop.error && candyMachineConfigured && <p className="terminal-error">RPC error: {drop.error}</p>}
            {lastSignature && <a className="receipt-link" href={`${config.explorer}/tx/${lastSignature}`} target="_blank" rel="noreferrer">VIEW LATEST RECEIPT ↗</a>}
          </article>
          <aside className="mint-readout">
            <article><p>CONNECTED WALLET</p><strong>{wallet.publicKey ? shortAddress(wallet.publicKey.toBase58()) : 'NO WALLET'}</strong><small>{wallet.connected ? 'IDENTITY RECOGNIZED' : 'CONNECT TO STEP UP'}</small></article>
            <article><p>COOKIE BALANCE</p><strong>{balance == null ? '—' : balance.toFixed(4)} <em>COOK</em></strong><small>NATIVE NETWORK BALANCE</small></article>
            <article className="collection-check"><p>COLLECTION CHECK</p><strong>{config.candyMachine ? shortAddress(config.candyMachine) : 'PENDING'}</strong><a href={config.explorer} target="_blank" rel="noreferrer">OPEN COOKIESCAN ↗</a></article>
          </aside>
        </section>

        <section className="arcade-aisle" id="registry"><div><b>03</b><span>THE TRAIT WALL</span></div><i /></section>
        <section className="trait-wall wrap">
          <div className="trait-copy"><p className="arcade-label">FINALIZED REGISTRY</p><h2>Sharp art. <em>Clean rules.</em></h2><p>Cookie Chain uses the original collection’s full-canvas composition system. The Cookboy Handheld remains the limited arm trait; Morsel and Cookiebox are sticker-only traits.</p></div>
          <div className="feature-strip">{featuredSweetardios.map((item, index) => <button type="button" key={item.id} className={index === featuredIndex ? 'draw-card selected' : 'draw-card'} onClick={() => setFeaturedIndex(index)}><img src={item.image} alt={`Select Sweetardio #${item.id}: ${item.name}`} /><span>#{item.id}</span><b>{item.name}</b><em>{item.traits[1]}</em></button>)}</div>
        </section>
      </main>

      <footer className="arcade-footer"><div className="wrap"><div className="sweetardio-lockup"><span><b>SWEET</b><em>ARDIO</em></span><small>COOKIE CHAIN EDITION</small></div><p>© SWEETARDIO · 444 PIECE SIDE COLLECTION · COOKIE CHAIN</p><a href="#top">BACK TO THE COUNTER ↑</a></div></footer>
    </div>
  )
}

export default App
