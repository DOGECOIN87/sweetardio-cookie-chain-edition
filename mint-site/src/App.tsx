// Design: Original Sweetardio.fun reference — centered glass arcade hero, visible shop scene,
// thin cerise/cyan panel edge, compact status chip, scene-led aisles, and essential mint content.
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

type DropState = { loaded: boolean; itemsLoaded: number; itemsRedeemed: number; priceCook: number | null; treasury: string; error?: string }

const LAMPORTS_PER_COOK = 1_000_000_000
const featuredSweetardios = [
  { id: '152', name: 'Chocolate Doughnut', image: '/featured/152.png', traits: ['Nightly Wallet sticker', 'Legendary Chase'] },
  { id: '003', name: 'OG Gummy Bear', image: '/featured/003.png', traits: ['Out of Order sticker', 'Core'] },
  { id: '012', name: 'Waffle', image: '/featured/012.png', traits: ['Nightly Wallet sticker', 'Core'] },
  { id: '059', name: 'Rice Crispy Treat', image: '/featured/059.png', traits: ['Crying Tomato sticker', 'Core'] },
  { id: '066', name: 'Vanilla Ice Cream', image: '/featured/066.png', traits: ['Candy Shop sticker', 'Core'] },
] as const

function shortAddress(value: string) { return value.length > 12 ? `${value.slice(0, 5)}…${value.slice(-5)}` : value }

function Aisle({ number, label }: { number: string; label: string }) {
  return <div className="aisle"><span>AISE {number}</span><i /><b>{label}</b><i /></div>
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
    connection.getBalance(wallet.publicKey).then(value => setBalance(value / LAMPORTS_PER_COOK)).catch(() => setBalance(null))
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
  const focusMint = () => document.getElementById('mint')?.scrollIntoView({ behavior: 'smooth', block: 'start' })

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
        const result = await transactionBuilder().add(setComputeUnitLimit(umi, { units: 800_000 })).add(mintV2(umi, { candyMachine: candyMachine.publicKey, candyGuard: guard.publicKey, nftMint, collectionMint: candyMachine.collectionMint, collectionUpdateAuthority: candyMachine.authority, tokenStandard: candyMachine.tokenStandard, mintArgs: { solPayment: some({ destination: guard.guards.solPayment.value.destination }) } })).sendAndConfirm(umi, { confirm: { commitment: 'confirmed' } })
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

  return (
    <div className="scene" id="top">
      <div className="scene-image" aria-hidden="true" /><div className="scene-tint" aria-hidden="true" />
      <header className="site-nav"><a className="brand-lockup nav-edition-logo" href="#top" aria-label="Cookie Chain Edition home"><img src="/cookie-chain-edition-logo.png" alt="Cookie Chain Edition" /></a><nav aria-label="Primary navigation"><a href="#draw">Draw</a><a href="#mint">Mint</a></nav><div className="nav-wallet"><span className="network-state"><i /> COOKIE CHAIN EDITION</span><WalletMultiButton /></div></header>

      <main>
        <section className="hero-stage" aria-labelledby="hero-title"><div className="hero-panel">
          <div className="panel-top-line" aria-hidden="true" />
          <img className="edition-plaque" src="/cookie-chain-edition-logo.png" alt="Cookie Chain Edition" />
          <p className="hero-chip"><i /> FINALIZED EDITION <span>·</span> 444 UNIQUE TOKENS</p>
          <h1 id="hero-title"><span><b>SWEET</b><em>ARDIO</em></span><strong>COOKIE CHAIN EDITION</strong></h1>
          <p className="hero-description">444 Sweetardios, made for the Cookie Chain Edition.</p>
          <button type="button" className="hero-mint" onClick={focusMint}><span>↑</span> MINT WHEN READY <span>↑</span></button>
        </div></section>

        <Aisle number="01" label="THE DRAW" />
        <section className="draw-section wrap" id="draw">
          <article className="draw-frame"><div className="draw-art"><img src={featured.image} alt={`Cookie Chain Edition #${featured.id}: ${featured.name}`} /><span>#{featured.id}</span></div><div className="draw-details"><p>COOKIE CHAIN EDITION DRAW</p><h2>{featured.name}</h2><div><b>{featured.traits[1]}</b><span>{featured.traits[0]}</span></div></div></article>
          <div className="draw-selector" aria-label="Select a finalized Cookie Chain Edition draw">{featuredSweetardios.map((item, index) => <button type="button" key={item.id} className={index === featuredIndex ? 'active' : ''} onClick={() => setFeaturedIndex(index)} aria-pressed={index === featuredIndex}><img src={item.image} alt={`Select Cookie Chain Edition #${item.id}: ${item.name}`} /><span>#{item.id}</span></button>)}</div>
        </section>

        <Aisle number="02" label="THE MINT" />
        <section className="mint-section wrap" id="mint" aria-labelledby="mint-heading"><div className="mint-copy"><p className="section-label">ON-CHAIN MINT</p><h2 id="mint-heading">STEP UP.<br /><em>MINT CLEAN.</em></h2><p>The terminal protects each transaction by checking the active Candy Guard and configured treasury before minting.</p></div>
          <article className="mint-terminal"><header><div><p>COOKIE CHAIN EDITION MINT</p><strong>{mintReady ? 'MINT TERMINAL LIVE' : soldOut ? 'EDITION SOLD OUT' : 'AWAITING DEPLOYMENT'}</strong></div><span className={mintReady ? 'status live' : 'status'}>{mintReady ? 'READY' : 'SAFE MODE'}</span></header><div className="terminal-controls"><div className="quantity"><label htmlFor="mint-qty">QUANTITY</label><div><button type="button" onClick={() => setQty(value => Math.max(1, value - 1))} aria-label="Decrease mint quantity">−</button><output id="mint-qty">{qty}</output><button type="button" onClick={() => setQty(value => Math.min(config.maxPerTx, value + 1))} aria-label="Increase mint quantity">+</button></div></div><div className="price"><span>PRICE</span><strong>{qty * displayedPrice} <em>COOK</em></strong></div></div><div className="terminal-action">{!wallet.connected ? <WalletMultiButton className="wide-wallet" /> : <button className="hero-mint terminal-button" disabled={minting || !mintReady} onClick={mintSelected}>{soldOut ? 'EDITION SOLD OUT' : minting ? 'MINTING…' : `MINT ${qty} SWEETARDIO${qty > 1 ? 'S' : ''}`} <span>↗</span></button>}<small>MAX {config.maxPerTx} PER TRANSACTION</small></div>
          {notice && <p className="terminal-message success" role="status">{notice}</p>}
          {!candyMachineConfigured && <p className="terminal-message">Configure <code>VITE_CANDY_MACHINE</code> after creating the 444-item Candy Machine.</p>}
          {candyMachineConfigured && !treasuryConfigured && <p className="terminal-message">Configure <code>VITE_TREASURY</code> to the Candy Guard payment destination.</p>}
          {drop.loaded && treasuryConfigured && !treasuryMatches && <p className="terminal-message error">Safety lock: configured treasury differs from the on-chain Candy Guard destination.</p>}
          {drop.error && candyMachineConfigured && <p className="terminal-message error">RPC error: {drop.error}</p>}
          {lastSignature && <a className="receipt-link" href={`${config.explorer}/tx/${lastSignature}`} target="_blank" rel="noreferrer">VIEW LATEST RECEIPT ↗</a>}
          </article>
        </section>
      </main>

      <footer className="site-footer"><div className="wrap"><div className="brand-lockup"><span><b>SWEET</b><em>ARDIO</em></span><small>COOKIE CHAIN EDITION</small></div><p>© SWEETARDIO · COOKIE CHAIN EDITION · 444 PIECE SIDE COLLECTION</p><a href="#top">BACK TO TOP ↑</a></div></footer>
    </div>
  )
}

export default App
