-- =============================================
-- Rihla-AI Database Schema
-- =============================================

-- Destinations
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    name_fr VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    description_fr TEXT,
    description_ar TEXT,
    climate VARCHAR(50),
    best_season VARCHAR(100),
    visa_required BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Hotels
CREATE TABLE hotels (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    stars INTEGER CHECK (stars BETWEEN 1 AND 5),
    price_per_night DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TND',
    amenities TEXT[],
    description_fr TEXT,
    description_ar TEXT,
    address TEXT,
    category VARCHAR(50) CHECK (category IN ('budget', 'standard', 'luxury')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Flights
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE SET NULL,
    airline VARCHAR(100),
    flight_number VARCHAR(20),
    departure_date DATE,
    return_date DATE,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TND',
    class VARCHAR(20) DEFAULT 'economy' CHECK (class IN ('economy', 'business', 'first')),
    seats_available INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Activities / Excursions
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    name_fr VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255),
    description_fr TEXT,
    description_ar TEXT,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TND',
    duration_hours DECIMAL(4,1),
    category VARCHAR(50) CHECK (category IN ('cultural', 'adventure', 'relaxation', 'religious', 'nightlife', 'shopping', 'gastronomic')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Travel Programs (packages)
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    title_fr VARCHAR(255) NOT NULL,
    title_ar VARCHAR(255),
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    description_fr TEXT,
    description_ar TEXT,
    duration_days INTEGER,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TND',
    category VARCHAR(50) CHECK (category IN ('budget', 'standard', 'luxury', 'adventure', 'religious')),
    target_audience VARCHAR(50) CHECK (target_audience IN ('student', 'family', 'couple', 'business', 'young', 'senior', 'all')),
    includes TEXT[],
    hotel_id INTEGER REFERENCES hotels(id) ON DELETE SET NULL,
    flight_id INTEGER REFERENCES flights(id) ON DELETE SET NULL,
    max_participants INTEGER,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Program-Activities junction
CREATE TABLE program_activities (
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    day_number INTEGER,
    PRIMARY KEY (program_id, activity_id)
);

-- Clients
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    full_name VARCHAR(255),
    preferred_language VARCHAR(2) DEFAULT 'fr',
    profile_type VARCHAR(50) CHECK (profile_type IN ('student', 'business', 'family', 'young', 'senior', 'couple', 'unknown')),
    budget_preference VARCHAR(20) CHECK (budget_preference IN ('budget', 'standard', 'luxury', 'unknown')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Passports (extracted OCR data)
CREATE TABLE passports (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    passport_number VARCHAR(20),
    surname VARCHAR(100),
    given_names VARCHAR(200),
    nationality VARCHAR(100),
    date_of_birth DATE,
    sex VARCHAR(1),
    place_of_birth VARCHAR(100),
    date_of_issue DATE,
    date_of_expiry DATE,
    issuing_authority VARCHAR(200),
    mrz_line1 VARCHAR(50),
    mrz_line2 VARCHAR(50),
    raw_ocr_text TEXT,
    image_path TEXT,
    extracted_at TIMESTAMP DEFAULT NOW()
);

-- Bookings / Reservations
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'paid', 'cancelled')),
    num_travelers INTEGER DEFAULT 1,
    total_price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'TND',
    booking_date TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    channel VARCHAR(10) NOT NULL CHECK (channel IN ('whatsapp', 'email')),
    started_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'escalated')),
    topic VARCHAR(255),
    summary TEXT
);

-- Messages (persistent log)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('client', 'assistant')),
    content TEXT NOT NULL,
    channel VARCHAR(10),
    media_type VARCHAR(20) CHECK (media_type IN ('text', 'image', 'document')),
    media_url TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Recommendations log
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    program_id INTEGER REFERENCES programs(id) ON DELETE SET NULL,
    score DECIMAL(5,3),
    reason TEXT,
    was_accepted BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_programs_destination ON programs(destination_id);
CREATE INDEX idx_programs_active ON programs(is_active);
CREATE INDEX idx_programs_category ON programs(category);
CREATE INDEX idx_hotels_destination ON hotels(destination_id);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_bookings_client ON bookings(client_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_client ON conversations(client_id);
CREATE INDEX idx_passports_client ON passports(client_id);
