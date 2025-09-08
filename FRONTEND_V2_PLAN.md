# Frontend 2.0 - Plan Rozwoju z TDD

## 🎯 Cel projektu
Kompletna przebudowa frontendu aplikacji Speecher z implementacją:
- Systemu logowania i rejestracji użytkowników
- Zarządzania profilami użytkowników
- Systemu projektów z tagami
- Zarządzania nagraniami w kontekście projektów
- Nowego layoutu z menu bocznym

## 📋 GitHub Tracking
- **Milestone**: Frontend 2.0 - User Management & Projects
- **Labels**: `frontend-v2`, `tdd`
- **Issues**: #15-#22

## 🏗️ Architektura

### Struktura katalogów
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── AuthProvider.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Layout.tsx
│   ├── user/
│   │   ├── UserProfile.tsx
│   │   ├── ApiKeysManager.tsx
│   │   └── PasswordChange.tsx
│   ├── projects/
│   │   ├── ProjectList.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── ProjectForm.tsx
│   │   └── ProjectTags.tsx
│   └── recordings/
│       ├── RecordingList.tsx
│       ├── RecordingUpload.tsx
│       └── RecordingStatus.tsx
├── contexts/
│   ├── AuthContext.tsx
│   └── ProjectContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useProjects.ts
│   └── useRecordings.ts
├── services/
│   ├── authService.ts
│   ├── projectService.ts
│   └── recordingService.ts
└── tests/
    ├── auth/
    ├── projects/
    ├── recordings/
    └── layout/
```

## 🧪 Strategia TDD

### Faza 1: Testy autentykacji
**Issue #15**: 🔐 TDD: Authentication System
- `LoginForm.test.tsx` - walidacja formularza, obsługa błędów
- `RegisterForm.test.tsx` - rejestracja, walidacja danych
- `AuthContext.test.tsx` - zarządzanie stanem autentykacji
- `ProtectedRoute.test.tsx` - ochrona tras

### Faza 2: Testy profilu użytkownika
**Issue #16**: 👤 TDD: User Profile Management
- `UserProfile.test.tsx` - wyświetlanie i edycja profilu
- `PasswordChange.test.tsx` - zmiana hasła
- `ApiKeysManager.test.tsx` - zarządzanie kluczami API

### Faza 3: Testy projektów
**Issue #17**: 📁 TDD: Project Management System
- `ProjectList.test.tsx` - lista projektów
- `ProjectCreate.test.tsx` - tworzenie projektu
- `ProjectEdit.test.tsx` - edycja projektu
- `ProjectTags.test.tsx` - system tagów

### Faza 4: Testy nagrań
**Issue #18**: 🎤 TDD: Recording Management in Projects
- `RecordingList.test.tsx` - lista nagrań w projekcie
- `RecordingUpload.test.tsx` - upload plików
- `RecordingProcessing.test.tsx` - status przetwarzania

### Faza 5: Testy layoutu
**Issue #19**: 🎨 TDD: Sidebar Navigation & Layout
- `Sidebar.test.tsx` - menu boczne
- `Navigation.test.tsx` - nawigacja
- `Layout.test.tsx` - responsywność

## 🔌 Backend API

**Issue #20**: Backend API Integration

### Endpoints
```
Authentication:
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/refresh
POST   /api/auth/logout

Users:
GET    /api/users/profile
PUT    /api/users/profile
PUT    /api/users/password
GET    /api/users/api-keys
POST   /api/users/api-keys
DELETE /api/users/api-keys/:id

Projects:
GET    /api/projects
POST   /api/projects
GET    /api/projects/:id
PUT    /api/projects/:id
DELETE /api/projects/:id
GET    /api/projects/:id/recordings
POST   /api/projects/:id/recordings
GET    /api/projects/:id/tags
POST   /api/projects/:id/tags
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7)
);

-- Recordings table (rozszerzenie istniejącej)
ALTER TABLE recordings 
ADD COLUMN project_id UUID REFERENCES projects(id),
ADD COLUMN user_id UUID REFERENCES users(id);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    key_hash VARCHAR(255) NOT NULL,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🛠️ Stack technologiczny

### Frontend
- **Framework**: React 18 + TypeScript
- **Routing**: React Router v6
- **State Management**: Context API + useReducer (lub Zustand)
- **Forms**: React Hook Form + Zod
- **UI Library**: Tailwind CSS + Headless UI
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Playwright

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (PyJWT)
- **Validation**: Pydantic

## 📅 Harmonogram

### Tydzień 1-2: Autentykacja
- [ ] Napisanie testów autentykacji
- [ ] Implementacja komponentów logowania/rejestracji
- [ ] Backend endpoints dla auth
- [ ] Integracja JWT

### Tydzień 3: Profile użytkowników
- [ ] Testy profilu użytkownika
- [ ] Komponenty profilu
- [ ] API keys management
- [ ] Backend dla użytkowników

### Tydzień 4-5: System projektów
- [ ] Testy projektów
- [ ] CRUD projektów
- [ ] System tagów
- [ ] Backend dla projektów

### Tydzień 6: Nagrania w projektach
- [ ] Testy nagrań
- [ ] Integracja z istniejącym systemem
- [ ] Przypisywanie do projektów
- [ ] Historia nagrań

### Tydzień 7: Layout i nawigacja
- [ ] Testy layoutu
- [ ] Sidebar implementation
- [ ] Responsive design
- [ ] User experience polish

### Tydzień 8: Finalizacja
- [ ] E2E testy (#21)
- [ ] Dokumentacja (#22)
- [ ] Performance optimization
- [ ] Deployment

## 🎯 Definition of Done

Każde zadanie uznajemy za ukończone gdy:
1. ✅ Wszystkie testy jednostkowe przechodzą
2. ✅ Kod przeszedł code review
3. ✅ Dokumentacja jest zaktualizowana
4. ✅ Nie ma błędów lintingu
5. ✅ Feature działa na wszystkich wspieranych przeglądarkach
6. ✅ Jest responsywny (mobile/tablet/desktop)

## 🚀 Rozpoczęcie pracy

1. Checkout na nowy branch:
   ```bash
   git checkout -b feature/frontend-v2
   ```

2. Instalacja zależności:
   ```bash
   npm install --save-dev @testing-library/react @testing-library/jest-dom
   npm install react-router-dom react-hook-form zod axios
   ```

3. Rozpoczęcie od testów (TDD):
   ```bash
   npm test -- --watch
   ```

## 📝 Notatki

- Priorytet: Najpierw testy, potem implementacja (TDD)
- Każdy PR powinien być linkowany do odpowiedniego issue
- Regularne code review i pair programming
- Dokumentacja na bieżąco

## 🔗 Linki

- [GitHub Issues](https://github.com/rafeekpro/speecher/issues?q=is%3Aissue+label%3Afrontend-v2)
- [Milestone](https://github.com/rafeekpro/speecher/milestone/1)