-- =============================================
-- Rihla-AI Sample Data (Seed) - Prix en TND réalistes
-- =============================================

-- Destinations
INSERT INTO destinations (name_fr, name_ar, country, city, description_fr, description_ar, climate, best_season, visa_required) VALUES
('Istanbul', 'اسطنبول', 'Turquie', 'Istanbul', 'Istanbul, la ville qui relie l''Europe et l''Asie, offre une richesse culturelle incomparable avec ses mosquées majestueuses, ses bazars animés et sa cuisine délicieuse.', 'اسطنبول، المدينة التي تربط أوروبا وآسيا، تقدم ثراءً ثقافياً لا مثيل له بمساجدها الفخمة وأسواقها النابضة بالحياة ومطبخها اللذيذ.', 'Méditerranéen', 'Printemps, Automne', FALSE),
('Dubai', 'دبي', 'Émirats Arabes Unis', 'Dubai', 'Dubai, la ville du luxe et de la modernité, offre des gratte-ciels impressionnants, des centres commerciaux géants et des expériences uniques dans le désert.', 'دبي، مدينة الفخامة والحداثة، تقدم ناطحات سحاب مذهلة ومراكز تسوق عملاقة وتجارب فريدة في الصحراء.', 'Désertique', 'Hiver', FALSE),
('Paris', 'باريس', 'France', 'Paris', 'Paris, la ville lumière, est célèbre pour la Tour Eiffel, le Louvre, sa gastronomie raffinée et son ambiance romantique.', 'باريس، مدينة النور، مشهورة ببرج إيفل ومتحف اللوفر ومطبخها الراقي وأجوائها الرومانسية.', 'Océanique', 'Printemps, Été', TRUE),
('La Mecque', 'مكة المكرمة', 'Arabie Saoudite', 'La Mecque', 'La Mecque, la ville sainte de l''Islam, accueille des millions de pèlerins chaque année pour le Hajj et la Omra.', 'مكة المكرمة، المدينة المقدسة في الإسلام، تستقبل ملايين الحجاج كل عام لأداء فريضة الحج والعمرة.', 'Désertique', 'Toute l''année', TRUE),
('Marrakech', 'مراكش', 'Maroc', 'Marrakech', 'Marrakech, la ville rouge, séduit par ses souks colorés, ses riads traditionnels, la place Jemaa el-Fna et les montagnes de l''Atlas à proximité.', 'مراكش، المدينة الحمراء، تسحر بأسواقها الملونة ورياضاتها التقليدية وساحة جامع الفنا وجبال الأطلس القريبة.', 'Semi-aride', 'Printemps, Automne', FALSE),
('Antalya', 'أنطاليا', 'Turquie', 'Antalya', 'Antalya, la perle de la Riviera turque, offre des plages magnifiques, des eaux turquoise et des complexes hôteliers tout inclus en bord de mer.', 'أنطاليا، جوهرة الريفييرا التركية، تقدم شواطئ رائعة ومياهاً فيروزية ومنتجعات شاملة على الشاطئ.', 'Méditerranéen', 'Été', FALSE),
('Le Caire', 'القاهرة', 'Égypte', 'Le Caire', 'Le Caire, la capitale de l''Égypte, est le berceau de la civilisation pharaonique avec les pyramides de Gizeh, le Sphinx et le musée égyptien.', 'القاهرة، عاصمة مصر، مهد الحضارة الفرعونية مع أهرامات الجيزة وأبو الهول والمتحف المصري.', 'Désertique', 'Automne, Hiver', TRUE),
('Rome', 'روما', 'Italie', 'Rome', 'Rome, la ville éternelle, regorge de trésors historiques : le Colisée, le Vatican, la Fontaine de Trevi et une gastronomie italienne incomparable.', 'روما، المدينة الأبدية، تزخر بكنوز تاريخية: الكولوسيوم، الفاتيكان، نافورة تريفي ومطبخ إيطالي لا مثيل له.', 'Méditerranéen', 'Printemps, Automne', TRUE);

-- Hotels
INSERT INTO hotels (destination_id, name, stars, price_per_night, currency, amenities, description_fr, description_ar, address, category) VALUES
-- Istanbul
(1, 'Istanbul Budget Hostel', 2, 95, 'TND', ARRAY['wifi', 'petit-dejeuner'], 'Auberge économique au cœur de Sultanahmet, idéale pour les étudiants et voyageurs à petit budget.', 'نزل اقتصادي في قلب السلطان أحمد، مثالي للطلاب والمسافرين بميزانية محدودة.', 'Sultanahmet, Istanbul', 'budget'),
(1, 'Grand Istanbul Hotel', 4, 320, 'TND', ARRAY['wifi', 'piscine', 'spa', 'restaurant', 'salle-de-sport'], 'Hôtel 4 étoiles avec vue sur le Bosphore, parfait pour les voyages d''affaires et les couples.', 'فندق 4 نجوم مع إطلالة على البوسفور، مثالي لرحلات العمل والأزواج.', 'Taksim, Istanbul', 'luxury'),
-- Dubai
(2, 'Dubai Backpackers', 2, 145, 'TND', ARRAY['wifi', 'climatisation'], 'Hébergement économique à Deira, proche des souks traditionnels.', 'إقامة اقتصادية في ديرة، قريبة من الأسواق التقليدية.', 'Deira, Dubai', 'budget'),
(2, 'Burj Al Arab View Hotel', 5, 1100, 'TND', ARRAY['wifi', 'piscine', 'spa', 'restaurant', 'vue-mer', 'room-service'], 'Hôtel 5 étoiles de luxe avec vue sur le Burj Al Arab, service exceptionnel.', 'فندق 5 نجوم فاخر مع إطلالة على برج العرب، خدمة استثنائية.', 'Jumeirah, Dubai', 'luxury'),
-- Paris
(3, 'Auberge de Jeunesse Paris', 2, 125, 'TND', ARRAY['wifi', 'petit-dejeuner'], 'Auberge de jeunesse proche du Quartier Latin, ambiance conviviale.', 'بيت شباب قريب من الحي اللاتيني، أجواء ودية.', 'Quartier Latin, Paris', 'budget'),
(3, 'Hotel Le Marais Paris', 4, 580, 'TND', ARRAY['wifi', 'restaurant', 'bar', 'conciergerie'], 'Hôtel élégant dans le Marais, à distance de marche des principaux monuments.', 'فندق أنيق في حي الماري، على مسافة قريبة من المعالم الرئيسية.', 'Le Marais, Paris', 'luxury'),
-- La Mecque
(4, 'Hotel Ajyad Makkah', 3, 420, 'TND', ARRAY['wifi', 'navette-haram', 'restaurant'], 'Hôtel à proximité du Haram, idéal pour les pèlerins, service de navette inclus.', 'فندق بالقرب من الحرم، مثالي للحجاج، خدمة نقل مكوكي مشمولة.', 'Ajyad, La Mecque', 'standard'),
-- Marrakech
(5, 'Riad Jemaa', 3, 190, 'TND', ARRAY['wifi', 'piscine', 'terrasse', 'petit-dejeuner'], 'Riad traditionnel avec patio, à 5 minutes de la place Jemaa el-Fna.', 'رياض تقليدي مع فناء، على بعد 5 دقائق من ساحة جامع الفنا.', 'Medina, Marrakech', 'standard'),
-- Antalya
(6, 'Antalya Beach Resort', 4, 280, 'TND', ARRAY['wifi', 'piscine', 'plage-privee', 'tout-inclus', 'animation', 'spa'], 'Complexe 4 étoiles tout inclus en bord de mer avec animation et sports nautiques.', 'منتجع 4 نجوم شامل على شاطئ البحر مع ترفيه ورياضات مائية.', 'Lara Beach, Antalya', 'standard'),
(6, 'Titanic Deluxe Belek', 5, 520, 'TND', ARRAY['wifi', 'piscine', 'plage-privee', 'tout-inclus', 'golf', 'spa', 'casino'], 'Resort 5 étoiles ultra-luxe avec golf, spa et plage privée, service royal.', 'منتجع 5 نجوم فاخر مع ملعب غولف وسبا وشاطئ خاص وخدمة ملكية.', 'Belek, Antalya', 'luxury'),
-- Le Caire
(7, 'Cairo Budget Inn', 2, 75, 'TND', ARRAY['wifi', 'climatisation'], 'Hôtel économique au centre du Caire, proche des transports en commun.', 'فندق اقتصادي في وسط القاهرة، قريب من وسائل المواصلات.', 'Centre ville, Le Caire', 'budget'),
(7, 'Marriott Mena House', 5, 680, 'TND', ARRAY['wifi', 'piscine', 'spa', 'restaurant', 'vue-pyramides', 'golf'], 'Hôtel historique 5 étoiles avec vue directe sur les Pyramides de Gizeh, expérience unique.', 'فندق تاريخي 5 نجوم مع إطلالة مباشرة على أهرامات الجيزة، تجربة فريدة.', 'Gizeh, Le Caire', 'luxury'),
-- Rome
(8, 'Rome Hostel Trastevere', 2, 110, 'TND', ARRAY['wifi', 'petit-dejeuner'], 'Auberge sympathique dans le quartier animé de Trastevere, proche du Colisée.', 'نزل ودي في حي تراستيفيري الصاخب، قريب من الكولوسيوم.', 'Trastevere, Rome', 'budget'),
(8, 'Hotel Artemide Roma', 4, 490, 'TND', ARRAY['wifi', 'restaurant', 'bar', 'spa', 'rooftop'], 'Hôtel 4 étoiles élégant sur la Via Nazionale avec rooftop et spa.', 'فندق 4 نجوم أنيق على شارع فيا ناتسيونالي مع مطعم سطح وسبا.', 'Via Nazionale, Rome', 'luxury');

-- Flights
INSERT INTO flights (origin, destination_id, airline, flight_number, departure_date, return_date, price, currency, class, seats_available) VALUES
('Tunis', 1, 'Tunisair', 'TU1050', '2026-06-15', '2026-06-22', 750, 'TND', 'economy', 120),
('Tunis', 1, 'Turkish Airlines', 'TK654', '2026-06-15', '2026-06-22', 1950, 'TND', 'business', 30),
('Tunis', 2, 'Emirates', 'EK752', '2026-07-01', '2026-07-08', 1100, 'TND', 'economy', 80),
('Tunis', 3, 'Air France', 'AF1455', '2026-05-20', '2026-05-27', 850, 'TND', 'economy', 100),
('Tunis', 4, 'Saudi Airlines', 'SV801', '2026-08-01', '2026-08-15', 980, 'TND', 'economy', 200),
('Tunis', 5, 'Royal Air Maroc', 'AT500', '2026-06-10', '2026-06-17', 520, 'TND', 'economy', 90),
('Tunis', 6, 'Tunisair', 'TU2080', '2026-07-05', '2026-07-12', 680, 'TND', 'economy', 150),
('Tunis', 6, 'Pegasus Airlines', 'PC970', '2026-08-10', '2026-08-17', 590, 'TND', 'economy', 180),
('Tunis', 7, 'EgyptAir', 'MS723', '2026-05-15', '2026-05-22', 650, 'TND', 'economy', 110),
('Tunis', 8, 'Tunisair', 'TU3020', '2026-04-25', '2026-04-30', 620, 'TND', 'economy', 90),
('Tunis', 8, 'Alitalia', 'AZ1180', '2026-09-10', '2026-09-15', 720, 'TND', 'economy', 80);

-- Activities
INSERT INTO activities (destination_id, name_fr, name_ar, description_fr, description_ar, price, currency, duration_hours, category) VALUES
-- Istanbul
(1, 'Visite de Sainte-Sophie', 'زيارة آيا صوفيا', 'Découvrez la majestueuse Sainte-Sophie, chef-d''œuvre architectural byzantin.', 'اكتشف آيا صوفيا المهيبة، تحفة العمارة البيزنطية.', 35, 'TND', 2, 'cultural'),
(1, 'Croisière sur le Bosphore', 'رحلة بحرية في البوسفور', 'Admirez Istanbul depuis le Bosphore lors d''une croisière panoramique.', 'استمتع بإسطنبول من البوسفور خلال رحلة بحرية بانورامية.', 60, 'TND', 3, 'adventure'),
(1, 'Shopping au Grand Bazar', 'تسوق في البازار الكبير', 'Explorez le Grand Bazar, l''un des plus anciens marchés couverts au monde.', 'استكشف البازار الكبير، أحد أقدم الأسواق المغطاة في العالم.', 0, 'TND', 3, 'shopping'),
-- Dubai
(2, 'Safari dans le désert', 'سفاري في الصحراء', 'Aventure en 4x4 dans les dunes, dîner bédouin et spectacle.', 'مغامرة في الكثبان الرملية بسيارة الدفع الرباعي، عشاء بدوي وعروض.', 190, 'TND', 6, 'adventure'),
(2, 'Visite du Burj Khalifa', 'زيارة برج خليفة', 'Montez au sommet du plus haut bâtiment du monde et admirez la vue.', 'اصعد إلى قمة أطول مبنى في العالم واستمتع بالمنظر.', 125, 'TND', 2, 'cultural'),
-- Paris
(3, 'Tour Eiffel + Croisière Seine', 'برج إيفل + رحلة في نهر السين', 'Montez à la Tour Eiffel puis profitez d''une croisière sur la Seine.', 'اصعد برج إيفل ثم استمتع برحلة في نهر السين.', 145, 'TND', 4, 'cultural'),
(3, 'Visite du Louvre', 'زيارة متحف اللوفر', 'Explorez le musée du Louvre et ses chefs-d''œuvre, dont la Joconde.', 'استكشف متحف اللوفر وروائعه، بما في ذلك الموناليزا.', 70, 'TND', 3, 'cultural'),
-- La Mecque
(4, 'Omra guidée', 'عمرة مع مرشد', 'Accomplissez la Omra avec un guide religieux expérimenté.', 'أدِّ العمرة مع مرشد ديني ذي خبرة.', 140, 'TND', 4, 'religious'),
-- Marrakech
(5, 'Excursion Atlas', 'رحلة جبال الأطلس', 'Randonnée dans les montagnes de l''Atlas avec déjeuner berbère.', 'تنزه في جبال الأطلس مع غداء أمازيغي.', 115, 'TND', 8, 'adventure'),
-- Antalya
(6, 'Excursion Pamukkale', 'رحلة باموك قلعة', 'Visitez les terrasses calcaires blanches de Pamukkale et les ruines d''Hiérapolis.', 'زر المدرجات الجيرية البيضاء في باموكالي وأطلال هيرابوليس.', 145, 'TND', 10, 'cultural'),
(6, 'Sports Nautiques', 'رياضات مائية', 'Jet-ski, parachute ascensionnel et plongée sous-marine dans les eaux turquoise.', 'جت سكي، مظلة صاعدة وغوص في المياه الفيروزية.', 180, 'TND', 3, 'adventure'),
-- Le Caire
(7, 'Pyramides de Gizeh + Sphinx', 'أهرامات الجيزة وأبو الهول', 'Visitez les pyramides de Gizeh et le Sphinx avec guide officiel.', 'زر أهرامات الجيزة وأبو الهول مع مرشد رسمي.', 95, 'TND', 4, 'cultural'),
(7, 'Musée Égyptien + Marché Khan', 'المتحف المصري + خان الخليلي', 'Découvrez les trésors de Toutankhamon puis explorez le souk de Khan el-Khalili.', 'اكتشف كنوز توت عنخ آمون ثم استكشف سوق خان الخليلي.', 80, 'TND', 5, 'cultural'),
-- Rome
(8, 'Colisée + Forum Romain', 'الكولوسيوم + المنتدى الروماني', 'Visitez le Colisée et le Forum Romain avec guide archéologue.', 'زر الكولوسيوم والمنتدى الروماني مع مرشد أثري.', 90, 'TND', 3, 'cultural'),
(8, 'Vatican + Chapelle Sixtine', 'الفاتيكان + كنيسة سيستين', 'Explorez les musées du Vatican, la Chapelle Sixtine et la basilique Saint-Pierre.', 'استكشف متاحف الفاتيكان وكنيسة سيستين وبازيليكا القديس بطرس.', 105, 'TND', 4, 'cultural');

-- Programs
INSERT INTO programs (title_fr, title_ar, destination_id, description_fr, description_ar, duration_days, price, currency, category, target_audience, includes, hotel_id, flight_id, max_participants, start_date, end_date, is_active) VALUES
-- Istanbul Budget (étudiants)
('Istanbul Découverte - Budget', 'اكتشف اسطنبول - اقتصادي', 1,
 'Programme économique de 7 jours à Istanbul. Hébergement en auberge, visites culturelles et gastronomie locale. Parfait pour les étudiants et jeunes voyageurs.',
 'برنامج اقتصادي لمدة 7 أيام في اسطنبول. إقامة في نزل، زيارات ثقافية ومأكولات محلية. مثالي للطلاب والمسافرين الشباب.',
 7, 2100, 'TND', 'budget', 'student',
 ARRAY['vol aller-retour', 'hébergement 7 nuits', 'petit-déjeuner', 'transfert aéroport', 'visite Sainte-Sophie', 'croisière Bosphore'],
 1, 1, 30, '2026-06-15', '2026-06-22', TRUE),

-- Istanbul Luxe (business)
('Istanbul Premium - Business', 'اسطنبول بريميوم - أعمال', 1,
 'Séjour haut de gamme de 7 jours à Istanbul. Hôtel 4 étoiles vue Bosphore, transferts VIP, visites privées et dîners gastronomiques.',
 'إقامة راقية لمدة 7 أيام في اسطنبول. فندق 4 نجوم مع إطلالة على البوسفور، نقل VIP، زيارات خاصة وعشاء فاخر.',
 7, 5200, 'TND', 'luxury', 'business',
 ARRAY['vol aller-retour business', 'hôtel 4 étoiles 7 nuits', 'pension complète', 'transfert VIP', 'guide privé', 'croisière privée Bosphore', 'dîner gastronomique'],
 2, 2, 15, '2026-06-15', '2026-06-22', TRUE),

-- Dubai Aventure (jeunes)
('Dubai Aventure', 'مغامرة دبي', 2,
 'Programme aventure de 7 jours à Dubai. Safari désert, visite du Burj Khalifa, parcs aquatiques et sorties nocturnes.',
 'برنامج مغامرة لمدة 7 أيام في دبي. سفاري صحراوي، زيارة برج خليفة، حدائق مائية وسهرات.',
 7, 3200, 'TND', 'adventure', 'young',
 ARRAY['vol aller-retour', 'hébergement 7 nuits', 'petit-déjeuner', 'safari désert', 'entrée Burj Khalifa', 'parc aquatique'],
 3, 3, 25, '2026-07-01', '2026-07-08', TRUE),

-- Dubai Luxe (couples)
('Dubai Royal Experience', 'تجربة دبي الملكية', 2,
 'Séjour de luxe 7 jours à Dubai. Hôtel 5 étoiles, expériences exclusives, yacht privé et shopping premium.',
 'إقامة فاخرة 7 أيام في دبي. فندق 5 نجوم، تجارب حصرية، يخت خاص وتسوق فاخر.',
 7, 11500, 'TND', 'luxury', 'couple',
 ARRAY['vol aller-retour', 'hôtel 5 étoiles 7 nuits', 'pension complète', 'transfert limousine', 'safari VIP', 'croisière yacht privé', 'entrée Burj Khalifa VIP'],
 4, 3, 10, '2026-07-01', '2026-07-08', TRUE),

-- Paris Culture (familles)
('Paris en Famille', 'باريس مع العائلة', 3,
 'Programme familial de 7 jours à Paris. Visites des monuments emblématiques, Disneyland Paris, et découverte gastronomique.',
 'برنامج عائلي لمدة 7 أيام في باريس. زيارة المعالم الشهيرة، ديزني لاند باريس، واكتشاف المطبخ.',
 7, 4800, 'TND', 'standard', 'family',
 ARRAY['vol aller-retour', 'hôtel 4 étoiles 7 nuits', 'petit-déjeuner', 'entrée Tour Eiffel', 'entrée Louvre', 'billet Disneyland', 'croisière Seine'],
 6, 4, 20, '2026-05-20', '2026-05-27', TRUE),

-- Omra (religieux)
('Omra Complète 15 jours', 'عمرة كاملة 15 يوم', 4,
 'Programme Omra complet de 15 jours avec hébergement proche du Haram, guide religieux, et visites des sites sacrés de La Mecque et Médine.',
 'برنامج عمرة كامل لمدة 15 يوماً مع إقامة قريبة من الحرم، مرشد ديني، وزيارة المواقع المقدسة في مكة والمدينة.',
 15, 6200, 'TND', 'religious', 'all',
 ARRAY['vol aller-retour', 'hôtel 15 nuits proche Haram', 'pension complète', 'guide religieux', 'navette Haram', 'visite Médine', 'visa Omra'],
 7, 5, 50, '2026-08-01', '2026-08-15', TRUE),

-- Marrakech (standard)
('Marrakech Authentique', 'مراكش الأصيلة', 5,
 'Programme de 7 jours à Marrakech. Riad traditionnel, excursion Atlas, souks, et gastronomie marocaine.',
 'برنامج 7 أيام في مراكش. رياض تقليدي، رحلة جبال الأطلس، أسواق، ومأكولات مغربية.',
 7, 2600, 'TND', 'standard', 'all',
 ARRAY['vol aller-retour', 'riad 7 nuits', 'petit-déjeuner', 'excursion Atlas', 'tour médina guidé', 'cours cuisine marocaine'],
 8, 6, 20, '2026-06-10', '2026-06-17', TRUE),

-- Antalya Tout Inclus (familles)
('Antalya Tout Inclus - Famille', 'أنطاليا شامل - عائلي', 6,
 'Séjour balnéaire tout inclus 7 jours à Antalya. Hôtel 4 étoiles en bord de mer, plage privée, animation et excursion Pamukkale.',
 'إقامة شاملة 7 أيام في أنطاليا. فندق 4 نجوم على شاطئ البحر، شاطئ خاص، ترفيه ورحلة إلى باموكالي.',
 7, 2800, 'TND', 'standard', 'family',
 ARRAY['vol aller-retour', 'hôtel 4 étoiles tout inclus 7 nuits', 'plage privée', 'animation', 'excursion Pamukkale', 'transfert aéroport'],
 9, 7, 40, '2026-07-05', '2026-07-12', TRUE),

-- Antalya Luxe (couples)
('Antalya Prestige', 'أنطاليا برستيج', 6,
 'Séjour luxueux 7 jours à Antalya dans un resort 5 étoiles. Spa, golf, plage privée et gastronomie internationale.',
 'إقامة فاخرة 7 أيام في أنطاليا في منتجع 5 نجوم. سبا وغولف وشاطئ خاص ومأكولات دولية.',
 7, 4500, 'TND', 'luxury', 'couple',
 ARRAY['vol aller-retour', 'resort 5 étoiles tout inclus 7 nuits', 'spa', 'golf', 'plage privée', 'transfert VIP'],
 10, 8, 20, '2026-08-10', '2026-08-17', TRUE),

-- Le Caire Découverte (budget)
('Le Caire & Pyramides', 'القاهرة والأهرامات', 7,
 'Découverte de 7 jours au Caire. Pyramides de Gizeh, Sphinx, musée égyptien et souk de Khan el-Khalili. Un voyage dans le temps.',
 'اكتشاف 7 أيام في القاهرة. أهرامات الجيزة، أبو الهول، المتحف المصري وسوق خان الخليلي. رحلة عبر الزمن.',
 7, 2100, 'TND', 'budget', 'all',
 ARRAY['vol aller-retour', 'hôtel 7 nuits', 'petit-déjeuner', 'visite pyramides', 'musée égyptien', 'souk Khan el-Khalili', 'guide francophone'],
 11, 9, 35, '2026-05-15', '2026-05-22', TRUE),

-- Rome Éternelle (culture)
('Rome Éternelle', 'روما الأبدية', 8,
 'Séjour culturel de 5 jours à Rome. Colisée, Vatican, Chapelle Sixtine, Fontaine de Trevi et gastronomie italienne authentique.',
 'إقامة ثقافية 5 أيام في روما. الكولوسيوم، الفاتيكان، كنيسة سيستين، نافورة تريفي ومأكولات إيطالية أصيلة.',
 5, 2400, 'TND', 'standard', 'all',
 ARRAY['vol aller-retour', 'hôtel 4 étoiles 5 nuits', 'petit-déjeuner', 'visite Colisée', 'Vatican + Chapelle Sixtine', 'guide francophone', 'transfert aéroport'],
 14, 10, 25, '2026-04-25', '2026-04-30', TRUE);

-- Program Activities
INSERT INTO program_activities (program_id, activity_id, day_number) VALUES
-- Istanbul Budget
(1, 1, 2), (1, 2, 4), (1, 3, 5),
-- Istanbul Luxe
(2, 1, 2), (2, 2, 3), (2, 3, 5),
-- Dubai Aventure
(3, 4, 3), (3, 5, 5),
-- Dubai Royal
(4, 4, 3), (4, 5, 2),
-- Paris Famille
(5, 6, 2), (5, 7, 4),
-- Omra
(6, 8, 2),
-- Marrakech
(7, 9, 4),
-- Antalya Famille
(8, 10, 4), (8, 11, 5),
-- Antalya Prestige
(9, 10, 3), (9, 11, 4),
-- Le Caire
(10, 12, 2), (10, 13, 4),
-- Rome
(11, 14, 2), (11, 15, 3);
