export const config = {
  rpc: import.meta.env.VITE_COOKIE_RPC || 'https://rpc.cookiescan.io',
  explorer: import.meta.env.VITE_COOKIE_EXPLORER || 'https://cookiescan.io',
  candyMachine: import.meta.env.VITE_CANDY_MACHINE || '',
  treasury: import.meta.env.VITE_TREASURY || '',
  displayPriceCook: Number(import.meta.env.VITE_MINT_PRICE_COOK || 10),
  maxPerTx: Math.max(1, Number(import.meta.env.VITE_MAX_PER_TX || 10)),
  totalSupply: 444,
} as const
