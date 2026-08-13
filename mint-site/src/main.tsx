import React, { useMemo } from 'react'
import ReactDOM from 'react-dom/client'
import { Buffer } from 'buffer'
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { NightlyWalletAdapter } from '@solana/wallet-adapter-nightly'
import '@solana/wallet-adapter-react-ui/styles.css'
import './styles.css'
import App from './App'
import { config } from './config'

globalThis.Buffer = Buffer

function Root() {
  const wallets = useMemo(() => [new NightlyWalletAdapter()], [])

  return (
    <ConnectionProvider endpoint={config.rpc}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <App />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><Root /></React.StrictMode>
)
