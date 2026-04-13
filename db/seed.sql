-- =============================================
-- Rihla-AI Sample Data (Seed)
-- =============================================

-- Destinations
INSERT INTO destinations (name_fr, name_ar, country, city, description_fr, description_ar, climate, best_season, visa_required) VALUES
('Istanbul', 'اسطنبول', 'Turquie', 'Istanbul', 'Istanbul, la ville qui relie l''Europe et l''Asie, offre une richesse culturelle incomparable avec ses mosquées majestueuses, ses bazars animés et sa cuisine délicieuse.', 'اسطنبول، المدينة التي تربط أوروبا وآسيا، تقدم ثراءً ثقافياً لا مثيل له بمساجدها الفخمة وأسواقها النابضة بالحياة ومطبخها اللذيذ.', 'Méditerranéen', 'Printemps, Automne', FALSE),
('Dubai', 'دبي', 'Émirats Arabes Unis', 'Dubai', 'Dubai, la ville du luxe et de la modernité, offre des gratte-ciels impressionnants, des centres commerciaux géants et des expériences uniques dans le désert.', 'دبي، مدينة الفخامة والحداثة، تقدم ناطحات سحاب مذهلة ومراكز تسوق عملاقة وتجارب فريدة في الصحراء.', 'Désertique', 'Hiver', FALSE),
('Paris', 'باريس', 'France', 'Paris', 'Paris, la ville lumière, est célèbre pour la Tour Eiffel, le Louvre, sa gastronomie raffinée et son ambiance romantique.', 'باريس، مدينة النور، مشهورة ببرج إيفل ومتحف اللوفر ومطبخها الراقي وأجوائها الرومانسية.', 'Océanique', 'Printemps, Été', TRUE),
('La Mecque', 'مكة المكرمة', 'Arabie Saoudite', 'La Mecque', 'La Mecque, la ville sainte de l''Islam, accueille des millions de pèlerins chaque année pour le Hajj et la Omra.', 'مكة المكرمة، المدينة المقدسة في الإسلام، تستقبل ملايين الحجاج كل عام لأداء فريضة الحج والعمرة.', 'Désertique', 'Toute l''année', TRUE),
('Marrakech', 'مراكش', 'Maroc', 'Marrakech', 'Marrakech, la ville rouge, séduit par ses souks colorés, ses riads traditionnels, la place Jemaa el-Fna et les montagnes de l''Atlas à proximité.', 'مراكش، المدينة الحمراء، تسحر بأسواقها الملونة ورياضاتها التقليدية وساحة جامع الفنا وجبال الأطلس القريبة.', 'Semi-aride', 'Printemps, Automne', FALSE);

-- Hotels
INSERT INTO hotels (destination_id, name, stars, price_per_night, currency, amenities, description_fr, description_ar, address, category) VALUES
-- Istanbul
(1, 'Istanbul Budget Hostel', 2, 3500, 'TND', ARRAY['wifi', 'petit-dejeuner'], 'Auberge économique au cœur de Sultanahmet, idéale pour les étudiants et voyageurs à petit budget.', 'نزل اقتصادي في قلب السلطان أحمد، مثالي للطلاب والمسافرين بميزانية محدودة.', 'Sultanahmet, Istanbul', 'budget'),
(1, 'Grand Istanbul Hotel', 4, 12000, 'TND', ARRAY['wifi', 'piscine', 'spa', 'restaurant', 'salle-de-sport'], 'Hôtel 4 étoiles avec vue sur le Bosphore, parfait pour les voyages d''affaires et les couples.', 'فندق 4 نجوم مع إطلالة على البوسفور، مثالي لرحلات العمل والأزواج.', 'Taksim, Istanbul', 'luxury'),
-- Dubai
(2, 'Dubai Backpackers', 2, 5000, 'TND', ARRAY['wifi', 'climatisation'], 'Hébergement économique à Deira, proche des souks traditionnels.', 'إقامة اقتصادية في ديرة، قريبة من الأسواق التقليدية.', 'Deira, Dubai', 'budget'),
(2, 'Burj Al Arab View Hotel', 5, 35000, 'TND', ARRAY['wifi', 'piscine', 'spa', 'restaurant', 'vue-mer', 'room-service'], 'Hôtel 5 étoiles de luxe avec vue sur le Burj Al Arab, service exceptionnel.', 'فندق 5 نجوم فاخر مع إطلالة على برج العرب، خدمة استثنائية.', 'Jumeirah, Dubai', 'luxury'),
-- Paris
(3, 'Auberge de Jeunesse Paris', 2, 6000, 'TND', ARRAY['wifi', 'petit-dejeuner'], 'Auberge de jeunesse proche du Quartier Latin, ambiance conviviale.', 'بيت شباب قريب من الحي اللاتيني، أجواء ودية.', 'Quartier Latin, Paris', 'budget'),
(3, 'Hotel Le Marais Paris', 4, 25000, 'TND', ARRAY['wifi', 'restaurant', 'bar', 'conciergerie'], 'Hôtel élégant dans le Marais, à distance de marche des principaux monuments.', 'فندق أنيق في حي الماري، على مسافة قريبة من المعالم الرئيسية.', 'Le Marais, Paris', 'luxury'),
-- La Mecque
(4, 'Hotel Ajyad Makkah', 3, 15000, 'TND', ARRAY['wifi', 'navette-haram', 'restaurant'], 'Hôtel à proximité du Haram, idéal pour les pèlerins, service de navette inclus.', 'فندق بالقرب من الحرم، مثالي للحجاج، خدمة نقل مكوكي مشمولة.', 'Ajyad, La Mecque', 'standard'),
-- Marrakech
(5, 'Riad Jemaa', 3, 8000, 'TND', ARRAY['wifi', 'piscine', 'terrasse', 'petit-dejeuner'], 'Riad traditionnel avec patio, à 5 minutes de la place Jemaa el-Fna.', 'رياض تقليدي مع فناء، على بعد 5 دقائق من ساحة جامع الفنا.', 'Medina, Marrakech', 'standard');

-- Flights
INSERT INTO flights (origin, destination_id, airline, flight_number, departure_date, return_date, price, currency, class, seats_available) VALUES
('Tunis', 1, 'Tunisair', 'TU1050', '2026-06-15', '2026-06-22', 45000, 'TND', 'economy', 120),
('Tunis', 1, 'Turkish Airlines', 'TK654', '2026-06-15', '2026-06-22', 65000, 'TND', 'business', 30),
('Tunis', 2, 'Emirates', 'EK752', '2026-07-01', '2026-07-08', 85000, 'TND', 'economy', 80),
('Tunis', 3, 'Air France', 'AF1455', '2026-05-20', '2026-05-27', 55000, 'TND', 'economy', 100),
('Tunis', 4, 'Saudi Airlines', 'SV801', '2026-08-01', '2026-08-15', 120000, 'TND', 'economy', 200),
('Tunis', 5, 'Royal Air Maroc', 'AT500', '2026-06-10', '2026-06-17', 35000, 'TND', 'economy', 90);

-- Activities
INSERT INTO activities (destination_id, name_fr, name_ar, description_fr, description_ar, price, currency, duration_hours, category) VALUES
-- Istanbul
(1, 'Visite de Sainte-Sophie', 'زيارة آيا صوفيا', 'Découvrez la majestueuse Sainte-Sophie, chef-d''œuvre architectural byzantin.', 'اكتشف آيا صوفيا المهيبة، تحفة العمارة البيزنطية.', 2000, 'TND', 2, 'cultural'),
(1, 'Croisière sur le Bosphore', 'رحلة بحرية في البوسفور', 'Admirez Istanbul depuis le Bosphore lors d''une croisière panoramique.', 'استمتع بإسطنبول من البوسفور خلال رحلة بحرية بانورامية.', 5000, 'TND', 3, 'adventure'),
(1, 'Shopping au Grand Bazar', 'تسوق في البازار الكبير', 'Explorez le Grand Bazar, l''un des plus anciens marchés couverts au monde.', 'استكشف البازار الكبير، أحد أقدم الأسواق المغطاة في العالم.', 0, 'TND', 3, 'shopping'),
-- Dubai
(2, 'Safari dans le désert', 'سفاري في الصحراء', 'Aventure en 4x4 dans les dunes, dîner bédouin et spectacle.', 'مغامرة في الكثبان الرملية بسيارة الدفع الرباعي، عشاء بدوي وعروض.', 8000, 'TND', 6, 'adventure'),
(2, 'Visite du Burj Khalifa', 'زيارة برج خليفة', 'Montez au sommet du plus haut bâtiment du monde et admirez la vue.', 'اصعد إلى قمة أطول مبنى في العالم واستمتع بالمنظر.', 6000, 'TND', 2, 'cultural'),
-- Paris
(3, 'Tour Eiffel + Croisière Seine', 'برج إيفل + رحلة في نهر السين', 'Montez à la Tour Eiffel puis profitez d''une croisière sur la Seine.', 'اصعد برج إيفل ثم استمتع برحلة في نهر السين.', 7000, 'TND', 4, 'cultural'),
(3, 'Visite du Louvre', 'زيارة متحف اللوفر', 'Explorez le musée du Louvre et ses chefs-d''œuvre, dont la Joconde.', 'استكشف متحف اللوفر وروائعه، بما في ذلك الموناليزا.', 4000, 'TND', 3, 'cultural'),
-- La Mecque
(4, 'Omra guidée', 'عمرة مع مرشد', 'Accomplissez la Omra avec un guide religieux expérimenté.', 'أدِّ العمرة مع مرشد ديني ذي خبرة.', 5000, 'TND', 4, 'religious'),
-- Marrakech
(5, 'Excursion Atlas', 'رحلة جبال الأطلس', 'Randonnée dans les montagnes de l''Atlas avec déjeuner berbère.', 'تنزه في جبال الأطلس مع غداء أمازيغي.', 4000, 'TND', 8, 'adventure');

-- Programs
INSERT INTO programs (title_fr, title_ar, destination_id, description_fr, description_ar, duration_days, price, currency, category, target_audience, includes, hotel_id, flight_id, max_participants, start_date, end_date, is_active) VALUES
-- Istanbul Budget (étudiants)
('Istanbul Découverte - Budget', 'اكتشف اسطنبول - اقتصادي', 1, 'Programme économique de 7 jours à Istanbul. Hébergement en auberge, visites culturelles et gastronomie locale. Parfait pour les étudiants et jeunes voyageurs.', 'برنامج اقتصادي لمدة 7 أيام في اسطنبول. إقامة في نزل، زيارات ثقافية ومأكولات محلية. مثالي للطلاب والمسافرين الشباب.', 7, 65000, 'TND', 'budget', 'student', ARRAY['vol aller-retour', 'hébergement 7 nuits', 'petit-déjeuner', 'transfert aéroport', 'visite Sainte-Sophie', 'croisière Bosphore'], 1, 1, 30, '2026-06-15', '2026-06-22', TRUE),

-- Istanbul Luxe (business)
('Istanbul Premium - Business', 'اسطنبول بريميوم - أعمال', 1, 'Séjour haut de gamme de 7 jours à Istanbul. Hôtel 4 étoiles vue Bosphore, transferts VIP, visites privées et dîners gastronomiques.', 'إقامة راقية لمدة 7 أيام في اسطنبول. فندق 4 نجوم مع إطلالة على البوسفور، نقل VIP، زيارات خاصة وعشاء فاخر.', 7, 180000, 'TND', 'luxury', 'business', ARRAY['vol aller-retour business', 'hôtel 4 étoiles 7 nuits', 'pension complète', 'transfert VIP', 'guide privé', 'croisière privée Bosphore', 'dîner gastronomique'], 2, 2, 15, '2026-06-15', '2026-06-22', TRUE),

-- Dubai Aventure (jeunes)
('Dubai Aventure', 'مغامرة دبي', 2, 'Programme aventure de 7 jours à Dubai. Safari désert, visite du Burj Khalifa, parcs aquatiques et sorties nocturnes. Idéal pour les jeunes.', 'برنامج مغامرة لمدة 7 أيام في دبي. سفاري صحراوي، زيارة برج خليفة، حدائق مائية وسهرات. مثالي للشباب.', 7, 135000, 'TND', 'adventure', 'young', ARRAY['vol aller-retour', 'hébergement 7 nuits', 'petit-déjeuner', 'safari désert', 'entrée Burj Khalifa', 'parc aquatique'], 3, 3, 25, '2026-07-01', '2026-07-08', TRUE),

-- Dubai Luxe (couples/business)
('Dubai Royal Experience', 'تجربة دبي الملكية', 2, 'Séjour de luxe 7 jours à Dubai. Hôtel 5 étoiles, expériences exclusives, yacht privé et shopping premium.', 'إقامة فاخرة 7 أيام في دبي. فندق 5 نجوم، تجارب حصرية، يخت خاص وتسوق فاخر.', 7, 350000, 'TND', 'luxury', 'couple', ARRAY['vol aller-retour', 'hôtel 5 étoiles 7 nuits', 'pension complète', 'transfert limousine', 'safari VIP', 'croisière yacht privé', 'entrée Burj Khalifa VIP'], 4, 3, 10, '2026-07-01', '2026-07-08', TRUE),

-- Paris Culture (familles)
('Paris en Famille', 'باريس مع العائلة', 3, 'Programme familial de 7 jours à Paris. Visites des monuments emblématiques, Disneyland Paris, et découverte gastronomique adaptée aux enfants.', 'برنامج عائلي لمدة 7 أيام في باريس. زيارة المعالم الشهيرة، ديزني لاند باريس، واكتشاف المطبخ المناسب للأطفال.', 7, 180000, 'TND', 'standard', 'family', ARRAY['vol aller-retour', 'hôtel 4 étoiles 7 nuits', 'petit-déjeuner', 'entrée Tour Eiffel', 'entrée Louvre', 'billet Disneyland', 'croisière Seine'], 6, 4, 20, '2026-05-20', '2026-05-27', TRUE),

-- Omra (religieux)
('Omra Complète 15 jours', 'عمرة كاملة 15 يوم', 4, 'Programme Omra complet de 15 jours avec hébergement proche du Haram, guide religieux, et visites des sites sacrés de La Mecque et Médine.', 'برنامج عمرة كامل لمدة 15 يوماً مع إقامة قريبة من الحرم، مرشد ديني، وزيارة المواقع المقدسة في مكة والمدينة.', 15, 280000, 'TND', 'religious', 'all', ARRAY['vol aller-retour', 'hôtel 15 nuits proche Haram', 'pension complète', 'guide religieux', 'navette Haram', 'visite Médine', 'visa Omra'], 7, 5, 50, '2026-08-01', '2026-08-15', TRUE),

-- Marrakech (standard)
('Marrakech Authentique', 'مراكش الأصيلة', 5, 'Programme de 7 jours à Marrakech. Riad traditionnel, excursion Atlas, souks, et gastronomie marocaine. Une immersion totale.', 'برنامج 7 أيام في مراكش. رياض تقليدي، رحلة جبال الأطلس، أسواق، ومأكولات مغربية. انغماس تام.', 7, 95000, 'TND', 'standard', 'all', ARRAY['vol aller-retour', 'riad 7 nuits', 'petit-déjeuner', 'excursion Atlas', 'tour médina guidé', 'cours cuisine marocaine'], 8, 6, 20, '2026-06-10', '2026-06-17', TRUE);

-- Program Activities
INSERT INTO program_activities (program_id, activity_id, day_number) VALUES
-- Istanbul Budget
(1, 1, 2),  -- Sainte-Sophie jour 2
(1, 2, 4),  -- Croisière Bosphore jour 4
(1, 3, 5),  -- Grand Bazar jour 5
-- Istanbul Luxe
(2, 1, 2),
(2, 2, 3),
(2, 3, 5),
-- Dubai Aventure
(3, 4, 3),  -- Safari jour 3
(3, 5, 5),  -- Burj Khalifa jour 5
-- Dubai Royal
(4, 4, 3),
(4, 5, 2),
-- Paris Famille
(5, 6, 2),  -- Tour Eiffel + Seine jour 2
(5, 7, 4),  -- Louvre jour 4
-- Omra
(6, 8, 2),  -- Omra guidée jour 2
-- Marrakech
(7, 9, 4);  -- Excursion Atlas jour 4
