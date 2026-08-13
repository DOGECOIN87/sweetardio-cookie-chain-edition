/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_COOKIE_RPC?: string
  readonly VITE_COOKIE_EXPLORER?: string
  readonly VITE_CANDY_MACHINE?: string
  readonly VITE_TREASURY?: string
  readonly VITE_MINT_PRICE_COOK?: string
  readonly VITE_MAX_PER_TX?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
