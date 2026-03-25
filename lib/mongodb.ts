import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI;

let cached = (global as any).mongoose;

if (!cached) {
  cached = (global as any).mongoose = { conn: null, promise: null };
}

async function dbConnect() {
  const isValidMongoURI =
    MONGODB_URI &&
    (MONGODB_URI.startsWith('mongodb://') || MONGODB_URI.startsWith('mongodb+srv://'));

  if (!isValidMongoURI) {
    console.warn(
      'MONGODB_URI is not set or invalid. Skipping database connection. Please set a valid MongoDB URI in .env.local.'
    );
    return null;
  }

  if (cached.conn) {
    return cached.conn;
  }

  if (!cached.promise) {
    const opts = {
      bufferCommands: false,
    };

    cached.promise = mongoose.connect(MONGODB_URI, opts).then((mongoose) => {
      return mongoose;
    });
  }
  cached.conn = await cached.promise;
  return cached.conn;
}

export default dbConnect;