const { createProxyMiddleware } = require('http-proxy-middleware');
const proxy = createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
});
module.exports = function (app) {
  app.use('/login', proxy);
  app.use('/api/v1', proxy);
};
