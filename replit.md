# replit.md

## Overview

This is a modern contract management application built with React, TypeScript, and Express.js. The system provides collaborative contract editing, real-time commenting, version control, and AI-powered suggestions for legal document management.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter for client-side routing
- **State Management**: TanStack Query for server state, React hooks for local state
- **UI Components**: shadcn/ui component library with Radix UI primitives
- **Styling**: Tailwind CSS with CSS variables for theming
- **Build Tool**: Vite with hot module replacement

### Backend Architecture
- **Runtime**: Node.js with Express.js
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM
- **Real-time Communication**: WebSockets for collaborative features
- **Session Management**: connect-pg-simple for PostgreSQL-backed sessions

### Key Components

#### Database Layer
- **ORM**: Drizzle ORM with PostgreSQL dialect
- **Schema Location**: `/shared/schema.ts`
- **Core Tables**:
  - `users` - User authentication and profiles
  - `projects` - Project organization
  - `contracts` - Contract documents with versioning
  - `comments` - Threaded commenting system with position tracking
- **Database Provider**: Neon Database with serverless connection pooling

#### Authentication & Authorization
- Role-based access control with user roles
- Session-based authentication
- User profiles with avatar support

#### Real-time Collaboration
- WebSocket server for live collaboration
- Cursor position tracking for multiple users
- Real-time comment synchronization
- Presence awareness system

#### File Structure
```
/client - React frontend application
  /src
    /components - Reusable UI components
    /pages - Route components
    /hooks - Custom React hooks
    /lib - Utility functions and API client
    /types - TypeScript type definitions
/server - Express.js backend
/shared - Shared types and schemas between frontend/backend
```

## Data Flow

1. **User Authentication**: Session-based auth with PostgreSQL session store
2. **Project Management**: Hierarchical organization (Projects → Contracts)
3. **Contract Editing**: Real-time collaborative editing with WebSocket synchronization
4. **Comment System**: Position-aware comments with threading support
5. **Version Control**: Automatic versioning with change tracking
6. **AI Integration**: Prepared for AI suggestions and contract analysis

## External Dependencies

### Frontend Dependencies
- **UI**: @radix-ui components, lucide-react icons
- **Data Fetching**: @tanstack/react-query
- **Forms**: react-hook-form with @hookform/resolvers
- **Charts**: recharts for analytics visualization
- **Date Handling**: date-fns
- **Carousel**: embla-carousel-react

### Backend Dependencies
- **Database**: @neondatabase/serverless, drizzle-orm
- **WebSockets**: ws
- **Validation**: zod with drizzle-zod integration
- **Build**: esbuild for production builds

### Development Tools
- **Bundler**: Vite with React plugin
- **TypeScript**: Full type safety across frontend/backend
- **Database Migration**: drizzle-kit
- **Development**: tsx for TypeScript execution

## Deployment Strategy

### Production Build Process
1. Frontend: Vite builds React app to `/dist/public`
2. Backend: esbuild bundles Express server to `/dist/index.js`
3. Database: Drizzle migrations applied via `db:push` script

### Environment Configuration
- **Development**: Hot reloading with Vite dev server
- **Production**: Static file serving with Express
- **Database**: Environment variable `DATABASE_URL` required
- **Platform**: Optimized for Replit deployment with autoscale target

### Replit Configuration
- **Modules**: nodejs-20, web, postgresql-16
- **Build Command**: `npm run build`
- **Start Command**: `npm run start`
- **Development**: `npm run dev` with port 5000

## Changelog

Changelog:
- June 25, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.