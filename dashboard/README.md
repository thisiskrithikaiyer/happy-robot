# Run Next.js Dashboard

## Prerequisites
- Node.js 16+ installed
- API running on http://127.0.0.1:5000

## Local Development

1. Install dependencies:
```bash
cd dashboard
npm install
```

2. Create `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api
NEXT_PUBLIC_API_KEY=cdc33e44d693a3a58451898d4ec9df862c65b954
```

3. Run dev server:
```bash
npm run dev
```

4. Open browser to `http://localhost:3000`

## Production Build

```bash
npm run build
npm run start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Base URL of the Loads API
- `NEXT_PUBLIC_API_KEY`: API key for authentication

## Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```