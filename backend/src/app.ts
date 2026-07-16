import express from "express";
import cors from "cors";
import path from "path";
import { verifyRouter } from "./routes/verify.js";
import { adminRouter } from "./routes/admin/index.js";

export function createApp() {
  const databaseUrl = process.env.DATABASE_URL || "";
  console.log(`[env] DATABASE_URL=${databaseUrl || "<not set>"}`);

  if (databaseUrl.includes("localhost")) {
    console.error("[env] ERROR: DATABASE_URL points to localhost. Application will not start.");
    process.exit(1);
  }

  const app = express();

  app.use(
    cors({
      origin: process.env.CORS_ORIGIN ?? "http://localhost:5173",
      credentials: true,
    })
  );
  app.use(express.json({ limit: "2mb" }));
  app.use(
    "/uploads",
    (req, res, next) => {
      res.setHeader("Content-Security-Policy", "default-src 'none'; sandbox");
      res.setHeader("X-Content-Type-Options", "nosniff");
      next();
    },
    express.static(path.resolve(process.env.UPLOAD_DIR ?? "./uploads"))
  );

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok", service: "UniPay Verify API" });
  });

  app.use("/api/verify", verifyRouter);
  app.use("/api/admin", adminRouter);

  app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    console.error(err);
    res.status(500).json({ error: err.message || "Erreur serveur." });
  });

  return app;
}
