from six import iteritems

KIND_STREET_ADDRESS  = 1 << 0 # 'SA'
KIND_ROUTE           = 1 << 1 # 'RO'
KIND_INTERSECTION    = 1 << 2 # 'IN'
KIND_POLITICAL       = 1 << 3 # 'PO'
KIND_COUNTRY         = 1 << 4 # 'CO'
KIND_AAL1            = 1 << 5 # 'A1'
KIND_AAL2            = 1 << 6 # 'A2'
KIND_AAL3            = 1 << 7 # 'A3'
KIND_AAL4            = 1 << 8 # 'A4'
KIND_AAL5            = 1 << 9 # 'A5'
KIND_COLLOQUIAL_AREA = 1 << 10 # 'CA'
KIND_LOCALITY        = 1 << 11 # 'LO'
KIND_WARD            = 1 << 12 # 'WA'
KIND_SUBLOCALITY     = 1 << 13 # 'SL'
KIND_NEIGHBORHOOD    = 1 << 14 # 'NE'
KIND_PREMISE         = 1 << 15 # 'PR'
KIND_SUBPREMISE      = 1 << 16 # 'SP'
KIND_POSTAL_CODE     = 1 << 17 # 'PC'
KIND_NATURAL_FEATURE = 1 << 18 # 'NF'
KIND_AIRPORT         = 1 << 19 # 'AI'
KIND_PARK            = 1 << 20 # 'PA'
KIND_POI             = 1 << 21 # 'PI'
KIND_FLOOR           = 1 << 22 # 'FL'
KIND_ESTABLISHMENT   = 1 << 23 # 'ES'
KIND_PARKING         = 1 << 24 # 'PK'
KIND_POST_BOX        = 1 << 25 # 'PB'
KIND_POSTAL_TOWN     = 1 << 26 # 'PT'
KIND_ROOM            = 1 << 27 # 'RM'
KIND_STREET_NUMBER   = 1 << 28 # 'SN'
KIND_BUS_STATION     = 1 << 29 # 'BS'
KIND_TRAIN_STATION   = 1 << 30 # 'TS'
KIND_TRANSIT_STATION = 1 << 31 # 'TR'

KIND_KEY_TABLE = {
    KIND_STREET_ADDRESS: 'street_address',
    KIND_ROUTE: 'route',
    KIND_INTERSECTION: 'intersection',
    KIND_POLITICAL: 'political',
    KIND_COUNTRY: 'country',
    KIND_AAL1: 'administrative_area_level_1',
    KIND_AAL2: 'administrative_area_level_2',
    KIND_AAL3: 'administrative_area_level_3',
    KIND_AAL4: 'administrative_area_level_4',
    KIND_AAL5: 'administrative_area_level_5',
    KIND_COLLOQUIAL_AREA: 'colloquial_area',
    KIND_LOCALITY: 'locality',
    KIND_WARD: 'ward',
    KIND_SUBLOCALITY: 'sublocality',
    KIND_NEIGHBORHOOD: 'neighborhood',
    KIND_PREMISE: 'premise',
    KIND_SUBPREMISE: 'subpremise',
    KIND_POSTAL_CODE: 'postal_code',
    KIND_NATURAL_FEATURE: 'natural_feature',
    KIND_AIRPORT: 'airport',
    KIND_PARK: 'park',
    KIND_POI: 'point_of_interest',
    KIND_FLOOR: 'floor',
    KIND_ESTABLISHMENT: 'establishment',
    KIND_PARKING: 'parking',
    KIND_POST_BOX: 'post_box',
    KIND_POSTAL_TOWN: 'postal_town',
    KIND_ROOM: 'room',
    KIND_STREET_NUMBER: 'street_number',
    KIND_BUS_STATION: 'bus_station',
    KIND_TRAIN_STATION: 'train_station',
    KIND_TRANSIT_STATION: 'transit_station',
}

KEY_KIND_TABLE = dict([(v, k) for k, v in iteritems(KIND_KEY_TABLE)])

    # KIND_CHOICES = [
    #     (KIND_STREET_ADDRESS, 'Street address'),
    #     (KIND_ROUTE, 'Route'),
    #     (KIND_INTERSECTION, 'Intersection'),
    #     (KIND_POLITICAL, 'Political'),
    #     (KIND_COUNTRY, 'Country'),
    #     (KIND_AAL1, 'Administrative area level 1'),
    #     (KIND_AAL2, 'Administrative area level 2'),
    #     (KIND_AAL3, 'Administrative area level 3'),
    #     (KIND_AAL4, 'Administrative area level 4'),
    #     (KIND_AAL5, 'Administrative area level 5'),
    #     (KIND_COLLOQUIAL_AREA, 'Colloquial area'),
    #     (KIND_LOCALITY, 'Locality'),
    #     (KIND_WARD, 'Ward'),
    #     (KIND_SUBLOCALITY, 'Sublocality'),
    #     (KIND_NEIGHBORHOOD, 'Neighborhood'),
    #     (KIND_PREMISE, 'Premise'),
    #     (KIND_SUBPREMISE, 'Subpremise'),
    #     (KIND_POSTAL_CODE, 'Postal code'),
    #     (KIND_NATURAL_FEATURE, 'Natural feature'),
    #     (KIND_AIRPORT, 'Airport'),
    #     (KIND_PARK, 'Park'),
    #     (KIND_POI, 'Point of interest'),
    #     (KIND_FLOOR, 'Floor'),
    #     (KIND_ESTABLISHMENT, 'Establishment'),
    #     (KIND_PARKING, 'Parking'),
    #     (KIND_POST_BOX, 'Post box'),
    #     (KIND_POSTAL_TOWN, 'Postal town'),
    #     (KIND_ROOM, 'Room'),
    #     (KIND_STREET_NUMBER, 'Street number'),
    #     (KIND_BUS_STATION, 'Bus station'),
    #     (KIND_TRAIN_STATION, 'Train station'),
    #     (KIND_TRANSIT_STATION, 'Transit station'),
    # ]
