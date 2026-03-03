-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    name_ar TEXT,
    category TEXT NOT NULL CHECK (category IN ('sofa', 'table', 'rug', 'lamp', 'shelf', 'art', 'pillow', 'other')),
    price_sar DECIMAL(10,2) NOT NULL,
    image_urls TEXT[] NOT NULL DEFAULT '{}',
    dimensions_cm JSONB,
    supplier TEXT NOT NULL CHECK (supplier IN ('ikea', 'noon', 'west elm', 'alrugaib')),
    product_url TEXT NOT NULL,
    style_tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Bundles table
CREATE TABLE bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    style TEXT NOT NULL,
    budget_tier TEXT NOT NULL CHECK (budget_tier IN ('budget', 'mid', 'premium')),
    product_ids UUID[] NOT NULL DEFAULT '{}',
    reference_images TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_image_url TEXT NOT NULL,
    style TEXT,
    bundle_id UUID REFERENCES bundles(id),
    render_urls TEXT[] NOT NULL DEFAULT '{}',
    hotspots JSONB DEFAULT '[]',
    room_type TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Analytics events table
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    event_type TEXT NOT NULL,
    product_id UUID REFERENCES products(id),
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_products_style_tags ON products USING GIN(style_tags);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_supplier ON products(supplier);
CREATE INDEX idx_bundles_style ON bundles(style);
CREATE INDEX idx_sessions_created ON sessions(created_at DESC);
CREATE INDEX idx_analytics_session ON analytics_events(session_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_timestamp ON analytics_events(timestamp DESC);

-- Enable Row Level Security (but keep it permissive for POC)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE bundles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Allow all operations for POC (no auth)
CREATE POLICY "Allow all on products" ON products FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on bundles" ON bundles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on sessions" ON sessions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on analytics_events" ON analytics_events FOR ALL USING (true) WITH CHECK (true);
