interface CountryData {
  name: string;
  capital: string;
  continent: string;
  population: number;
  area_km2: number;
  languages: string[];
  currency: string;
  flag_emoji: string;
  fun_facts: string[];
  major_cities?: Array<{
    name: string;
    coordinates: { lat: number; lng: number };
  }>;
}

interface CountryInfoProps {
  country: CountryData;
  onClose?: () => void;
}

/**
 * CountryInfo Component
 * 
 * Displays detailed information about a selected country
 * Can be used in explore mode or after quiz completion
 */
export function CountryInfo({ country, onClose }: CountryInfoProps) {
  const formatPopulation = (pop: number) => {
    if (pop >= 1000000) {
      return `${(pop / 1000000).toFixed(2)} millones`;
    }
    return pop.toLocaleString();
  };

  const formatArea = (area: number) => {
    return `${area.toLocaleString()} km²`;
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-2xl mx-auto relative">
      {/* Close Button */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors"
        >
          ✕
        </button>
      )}

      {/* Header */}
      <div className="flex items-center space-x-4 mb-6 pb-4 border-b-2 border-gray-200">
        <div className="text-6xl">{country.flag_emoji}</div>
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-gray-900">{country.name}</h2>
          <p className="text-lg text-gray-600">{country.capital}</p>
        </div>
      </div>

      {/* Basic Info Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
          <div className="text-xs text-blue-700 font-medium mb-1">Continente</div>
          <div className="text-lg font-bold text-blue-900">{country.continent}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
          <div className="text-xs text-purple-700 font-medium mb-1">Población</div>
          <div className="text-lg font-bold text-purple-900">
            {formatPopulation(country.population)}
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
          <div className="text-xs text-green-700 font-medium mb-1">Área</div>
          <div className="text-lg font-bold text-green-900">
            {formatArea(country.area_km2)}
          </div>
        </div>
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-4">
          <div className="text-xs text-yellow-700 font-medium mb-1">Moneda</div>
          <div className="text-lg font-bold text-yellow-900">{country.currency}</div>
        </div>
      </div>

      {/* Languages */}
      <div className="mb-6">
        <h3 className="text-sm font-bold text-gray-700 mb-2">Idiomas</h3>
        <div className="flex flex-wrap gap-2">
          {country.languages.map((lang, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
            >
              {lang}
            </span>
          ))}
        </div>
      </div>

      {/* Major Cities */}
      {country.major_cities && country.major_cities.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-bold text-gray-700 mb-2">Ciudades Principales</h3>
          <div className="space-y-2">
            {country.major_cities.map((city, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 text-sm text-gray-700 bg-gray-50 rounded-lg p-2"
              >
                <span className="text-blue-500">📍</span>
                <span className="font-medium">{city.name}</span>
                <span className="text-xs text-gray-500">
                  ({city.coordinates.lat.toFixed(2)}°, {city.coordinates.lng.toFixed(2)}°)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fun Facts */}
      <div>
        <h3 className="text-sm font-bold text-gray-700 mb-2">Datos Curiosos 🎯</h3>
        <ul className="space-y-2">
          {country.fun_facts.map((fact, index) => (
            <li
              key={index}
              className="flex items-start space-x-2 text-sm text-gray-700"
            >
              <span className="text-yellow-500 mt-1">⭐</span>
              <span>{fact}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 pt-4 border-t-2 border-gray-200 flex gap-3">
        <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-2 px-4 rounded-xl hover:shadow-lg transition-all duration-200 text-sm">
          Ver en el Mapa 🗺️
        </button>
        <button className="flex-1 bg-white border-2 border-gray-300 text-gray-700 font-bold py-2 px-4 rounded-xl hover:border-gray-400 hover:shadow-md transition-all duration-200 text-sm">
          Más Información 📚
        </button>
      </div>
    </div>
  );
}
