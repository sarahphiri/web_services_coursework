import Navbar from "../components/Navbar";

async function getRecommendations() {
  const res = await fetch("http://127.0.0.1:8000/recommendations?limit=10", {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch recommendations");
  }

  return res.json();
}

function getCostLabel(cost: number) {
  if (cost < 120) return "Very affordable";
  if (cost < 200) return "Affordable";
  if (cost < 300) return "Moderate";
  return "Premium";
}

function getCrowdLabel(visitors: number) {
  if (visitors < 2) return "Very low";
  if (visitors < 5) return "Low";
  if (visitors < 8) return "Moderate";
  return "Busy";
}

export default async function RecommendationsPage() {
  const recommendations = await getRecommendations();

  return (
    <>
      <Navbar />

      <main className="min-h-screen px-6 py-10">
        <div className="max-w-6xl mx-auto">
          <div className="mb-10">
            <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-2">
              Smart destination discovery
            </p>
            <h1 className="text-4xl font-bold text-[#007788] mb-3">
              Recommended Destinations
            </h1>
            <p className="text-gray-700 max-w-2xl">
              Explore destinations selected for affordability, lower crowd
              levels, and quality — helping users make calmer and more informed
              travel decisions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
            {recommendations.map((destination: any, index: number) => (
              <div
                key={index}
                className="bg-white rounded-[1.5rem] overflow-hidden shadow-md border border-gray-100 hover:shadow-xl transition"
              >
                <div className="h-48 bg-gradient-to-br from-cyan-100 via-teal-100 to-sky-100 flex items-center justify-center">
                  <span className="text-6xl">🌍</span>
                </div>

                <div className="p-6">
                  <h2 className="text-2xl font-semibold mb-2 text-[#333333]">
                    {destination.name}
                  </h2>

                  <p className="text-gray-600 mb-4">
                    {destination.country} • {destination.continent}
                  </p>

                  <div className="grid grid-cols-2 gap-4 mb-5 text-sm">
                    <div className="bg-[#f9f9f9] rounded-xl p-3">
                      <p className="text-gray-500 mb-1">Affordability</p>
                      <p className="font-semibold text-[#00A896]">
                        {getCostLabel(destination.avg_cost_usd)}
                      </p>
                    </div>

                    <div className="bg-[#f9f9f9] rounded-xl p-3">
                      <p className="text-gray-500 mb-1">Crowd level</p>
                      <p className="font-semibold text-[#007788]">
                        {getCrowdLabel(destination.annual_visitors_m)}
                      </p>
                    </div>

                    <div className="bg-[#f9f9f9] rounded-xl p-3">
                      <p className="text-gray-500 mb-1">Rating</p>
                      <p className="font-semibold text-[#FFD166]">
                        ⭐ {destination.rating}
                      </p>
                    </div>

                    <div className="bg-[#f9f9f9] rounded-xl p-3">
                      <p className="text-gray-500 mb-1">Cost</p>
                      <p className="font-semibold text-[#333333]">
                        ${destination.avg_cost_usd}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-sm text-gray-600 mb-5">
                    <span>Type: {destination.type}</span>
                    <span>Season: {destination.best_season}</span>
                  </div>

                  <button className="w-full rounded-full bg-[#007788] text-white py-3 font-medium hover:bg-[#006674] transition">
                    View Destination
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}