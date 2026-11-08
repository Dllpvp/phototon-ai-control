import { lazy } from "react";
import { Navigate, type RouteObject } from "react-router";
import { createBrowserRouter, createHashRouter } from "react-router";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const JournalPage = lazy(() => import("./pages/JournalPage"));
const ReportPage = lazy(() => import("./pages/ReportPage"));
const DecisionPage = lazy(() => import("./pages/DecisionPage"));
const DevKit = lazy(() => import("./pages/DevKit"));

export const routes: RouteObject[] = [
  { path: "/", element: <Dashboard /> },
  { path: "/journal", element: <JournalPage /> },
  { path: "/report", element: <ReportPage /> },
  { path: "/decision/:id", element: <DecisionPage /> },
  { path: "/devkit", element: <DevKit /> },
  { path: "*", element: <Navigate to="/" replace /> },
];

const useHashRouter = import.meta.env.VITE_HASH_ROUTER === "1";

export const router = useHashRouter
  ? createHashRouter(routes)
  : createBrowserRouter(routes);