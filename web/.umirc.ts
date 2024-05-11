import { defineConfig } from 'umi';
import { appName } from './src/conf.json';
import routes from './src/routes';

export default defineConfig({
  title: appName,
  outputPath: 'dist',
  // alias: { '@': './src' },
  npmClient: 'npm',
  base: '/',
  routes,
  publicPath: '/',
  esbuildMinifyIIFE: true,
  icons: {},
  hash: true,
  favicons: ['/logo.svg'],
  clickToComponent: {},
  history: {
    type: 'browser',
  },
  plugins: ['@react-dev-inspector/umi4-plugin', '@umijs/plugins/dist/dva'],
  dva: {},

  lessLoader: {
    modifyVars: {
      hack: `true; @import "~@/less/index.less";`,
    },
  },
  devtool: 'source-map',
  copy: ['src/conf.json'],
  proxy: {
    '/v1': {
      target: 'http://123.60.95.134:9380/',
      changeOrigin: true,
      // pathRewrite: { '^/v1': '/v1' },
    },
  },
});
