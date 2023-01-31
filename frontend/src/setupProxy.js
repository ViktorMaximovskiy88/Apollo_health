const { createProxyMiddleware } = require('http-proxy-middleware');
const proxy = createProxyMiddleware({
  target: 'http://127.0.0.1:8000',
  changeOrigin: true,
});
module.exports = function (app) {
  app.use('/api/v1', proxy);
  app.use('/request-access', proxy);
};
