// Design: Cookie Chain arcade counter — asymmetric editorial hierarchy, restrained Sweetardio.fun
// neon, full-quality collection art, and conventional accessible mint controls.
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
  const soldOut = minted >= supply
  const displayedPrice = drop.priceCook ?? config.displayPriceCook
  const treasuryMatches = drop.treasury === config.treasury
  const mintReady = drop.loaded && candyMachineConfigured && treasuryConfigured && treasuryMatches && !soldOut
  const featured = featuredSweetardios[featuredIndex]

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
    <div className="site-shell" id="top">
      <div className="shop-background" aria-hidden="true" />
      <div className="site-wash" aria-hidden="true" />

      <header className="site-nav">
        <a className="brand-lockup" href="#top" aria-label="Sweetardio Cookie Chain Edition home"><span><b>SWEET</b><em>ARDIO</em></span><small>COOKIE CHAIN EDITION</small></a>
        <nav aria-label="Primary navigation"><a href="#edition">Edition</a><a href="#mint">Mint</a><a href="#registry">Traits</a></nav>
        <div className="nav-wallet"><span className="network-state"><i /> COOKIE CHAIN</span><WalletMultiButton /></div>
      </header>

      <main>
        <section className="hero wrap" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow"><span /> SWEETARDIO PRESENTS</p>
            <div className="logo-plaque"><img src="/cookie-chain-edition-logo.png" alt="Cookie Chain Edition" /></div>
            <h1 id="hero-title"><span><b>SWEET</b><em>ARDIO</em></span><strong>COOKIE CHAIN</strong></h1>
            <p className="hero-summary">A 444-piece side edition built from the original Sweetardio character system, released for the Cookie Chain.</p>
            <div className="hero-actions"><button type="button" className="primary-action" onClick={focusMint}>MINT THE EDITION <span>↓</span></button><a href="#edition" className="text-action">SEE THE DRAW <span>→</span></a></div>
            <div className="hero-facts" aria-label="Edition facts"><span><b>444</b> UNIQUE TOKENS</span><span><b>{remaining}</b> AVAILABLE</span><span><b>{displayedPrice}</b> COOK</span></div>
          </div>

          <aside className="hero-feature" aria-label="Featured finalized collection draw">
            <div className="feature-frame"><img src={featured.image} alt={`Sweetardio #${featured.id}: ${featured.name}`} /><span className="feature-index">#{featured.id}</span><span className="feature-stamp">FINAL RENDER</span></div>
            <div className="feature-caption"><div><p>CURATED DRAW</p><h2>{featured.name}</h2></div><span>{featured.traits[2]}</span></div>
            <p className="feature-traits">{featured.background} <i>•</i> {featured.traits[0]} <i>•</i> {featured.traits[1]}</p>
          </aside>
        </section>

        <section className="release-strip" aria-label="Collection release status"><div className="wrap"><span>FINALIZED COLLECTION</span><i /> <span>FULL-QUALITY SOURCE ART</span><i /> <span>COOKIE CHAIN EDITION</span></div></section>

        <section className="content-section wrap" id="edition">
          <div className="section-intro"><p className="eyebrow"><span /> 01 / THE EDITION</p><h2>Pick a card.<br /><em>Meet the cast.</em></h2><p>Each preview is a direct 1393px finalized render. Select a card to inspect the draw; the selection stays put until you choose another.</p></div>
          <div className="draw-grid" aria-label="Select a finalized collection draw">{featuredSweetardios.map((item, index) => <button type="button" key={item.id} className={index === featuredIndex ? 'draw-card active' : 'draw-card'} onClick={() => setFeaturedIndex(index)} aria-pressed={index === featuredIndex}><img src={item.image} alt={`Select Sweetardio #${item.id}: ${item.name}`} /><span>#{item.id}</span><strong>{item.name}</strong><em>{item.traits[2]}</em></button>)}</div>
        </section>

        <section className="mint-section" id="mint" aria-labelledby="mint-heading"><div className="wrap mint-layout">
          <div className="mint-intro"><p className="eyebrow"><span /> 02 / THE MINT COUNTER</p><h2 id="mint-heading">Step up<br /><em>when it is live.</em></h2><p>The mint terminal verifies the active Candy Guard and treasury destination before it permits a transaction.</p><dl><div><dt>SUPPLY</dt><dd>{supply}</dd></div><div><dt>REMAINING</dt><dd>{remaining}</dd></div><div><dt>STATUS</dt><dd>{mintReady ? 'LIVE' : soldOut ? 'SOLD OUT' : 'STAGED'}</dd></div></dl></div>
          <article className="mint-terminal">
            <div className="terminal-head"><div><p>COOKIE CHAIN MINT</p><strong>{mintReady ? 'MINT TERMINAL LIVE' : soldOut ? 'EDITION SOLD OUT' : 'AWAITING DEPLOYMENT'}</strong></div><span className={mintReady ? 'status-pill live' : 'status-pill'}>{mintReady ? 'READY' : 'SAFE MODE'}</span></div>
            <div className="terminal-controls"><div className="quantity-field"><label htmlFor="mint-qty">MINT QUANTITY</label><div><button type="button" onClick={() => setQty(value => Math.max(1, value - 1))} aria-label="Decrease mint quantity">−</button><output id="mint-qty">{qty}</output><button type="button" onClick={() => setQty(value => Math.min(config.maxPerTx, value + 1))} aria-label="Increase mint quantity">+</button></div><small>MAX {config.maxPerTx} PER TRANSACTION</small></div><div className="price-field"><span>COUNTER TOTAL</span><strong>{qty * displayedPrice} <em>COOK</em></strong><small>{drop.loaded ? 'CANDY GUARD PRICE' : 'TARGET MINT PRICE'}</small></div></div>
            <div className="terminal-action">{!wallet.connected ? <WalletMultiButton className="wide-wallet" /> : <button className="primary-action terminal-button" disabled={minting || !mintReady} onClick={mintSelected}>{soldOut ? 'EDITION SOLD OUT' : minting ? 'MINTING…' : `MINT ${qty} SWEETARDIO${qty > 1 ? 'S' : ''}`} <span>↗</span></button>}<p>Transactions activate only when the on-chain payment destination matches the configured treasury.</p></div>
            {notice && <p className="terminal-message success" role="status">{notice}</p>}
            {!candyMachineConfigured && <p className="terminal-message">Deployment mode: configure <code>VITE_CANDY_MACHINE</code> after creating the 444-item Candy Machine.</p>}
            {candyMachineConfigured && !treasuryConfigured && <p className="terminal-message">Deployment mode: configure <code>VITE_TREASURY</code> to the Candy Guard payment destination.</p>}
            {drop.loaded && treasuryConfigured && !treasuryMatches && <p className="terminal-message error">Safety lock: configured treasury differs from the on-chain Candy Guard destination.</p>}
            {drop.error && candyMachineConfigured && <p className="terminal-message error">RPC error: {drop.error}</p>}
            {lastSignature && <a className="receipt-link" href={`${config.explorer}/tx/${lastSignature}`} target="_blank" rel="noreferrer">VIEW LATEST RECEIPT ↗</a>}
          </article>
        </div></section>

        <section className="trait-section wrap" id="registry"><div className="trait-copy"><p className="eyebrow"><span /> 03 / TRAIT REGISTER</p><h2>Clear rules.<br /><em>Clean source art.</em></h2><p>Cookboy Handheld is the limited arm trait. Morsel and Cookiebox are sticker-only traits. The Cookboy emboss background retains its public trait name.</p></div><div className="trait-list"><div><b>STICKERS</b><span>Morsel · Cookiebox</span></div><div><b>ARM TRAIT</b><span>Cookboy Handheld</span></div><div><b>EMBOSS BG</b><span>Cookboy</span></div></div></section>
      </main>

      <footer className="site-footer"><div className="wrap"><div className="brand-lockup"><span><b>SWEET</b><em>ARDIO</em></span><small>COOKIE CHAIN EDITION</small></div><p>© SWEETARDIO · 444 PIECE SIDE COLLECTION</p><a href="#top">BACK TO TOP ↑</a></div></footer>
    </div>
  )
}

export default App
