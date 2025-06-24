import path from 'path';
import { defineConfig } from 'umi';
import { appName } from './src/conf.json';
import routes from './src/routes';

export default defineConfig({
  title: appName,
  outputPath: 'dist',
  alias: { '@parent': path.resolve(__dirname, '../') },
  npmClient: 'npm',
  base: '/',
  routes,
  publicPath: '/',
  hash: true,
  favicons: ['/logo.svg'],
  history: {
    type: 'browser',
  },
  plugins: ['@umijs/plugins/dist/tailwindcss'],
  jsMinifier: 'none',
  lessLoader: {
    modifyVars: {
      hack: `true; @import "~@/less/index.less";`,
    },
  },
  devtool: 'source-map',
  copy: [
    { from: 'src/conf.json', to: 'dist/conf.json' },
    { from: 'node_modules/monaco-editor/min/vs/', to: 'dist/vs/' },
  ],
  proxy: [
    {
      context: ['/api', '/v1'],
      target: 'http://127.0.0.1:9380/',
      changeOrigin: true,
      ws: true,
      logger: console,
    },
  ],
  tailwindcss: {},
});
