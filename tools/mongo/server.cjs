const path = require('path');
const fs = require('fs');
const { MongoMemoryServer } = require('mongodb-memory-server');
(async () => {
  const root = path.resolve(__dirname, '../..');
  const dbPath = path.join(root, '.local/mongo');
  fs.mkdirSync(dbPath, { recursive: true });
  const server = await MongoMemoryServer.create({
    binary: { version: '8.2.6', downloadDir: path.join(root, '.local/mongo-binaries') },
    instance: { port: Number(process.env.MONGO_PORT || 27017), dbPath, storageEngine: 'wiredTiger', ip: '127.0.0.1' },
  });
  console.log('Local MongoDB ready; data persists in .local/mongo');
  const stop = async () => { await server.stop({ doCleanup: false }); process.exit(0); };
  process.on('SIGTERM', stop); process.on('SIGINT', stop);
})().catch(error => { console.error(error.message); process.exit(1); });
