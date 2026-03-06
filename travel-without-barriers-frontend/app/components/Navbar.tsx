import Image from "next/image";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <Image
            src="/TWB_Logo.png"
            alt="TWB_Logo"
            width={56}
            height={56}
            className="object-contain"
          />
          <div>
            <p className="text-xl font-bold text-[#007788] leading-none">
              Travel
            </p>
            <p className="text-sm tracking-wide text-gray-600 leading-none">
              Without Barriers
            </p>
          </div>
        </a>

        <div className="flex items-center gap-6 text-sm font-medium">
          <a href="/" className="text-gray-700 hover:text-[#007788] transition">
            Home
          </a>
          <a
            href="/recommendations"
            className="text-gray-700 hover:text-[#007788] transition"
          >
            Recommendations
          </a>
          <a
            href="/wishlists"
            className="text-gray-700 hover:text-[#007788] transition"
          >
            Wishlists
          </a>
          <a
            href="/wishlists"
            className="px-4 py-2 rounded-full bg-[#007788] text-white hover:bg-[#006674] transition shadow-sm"
          >
            Plan a Trip
          </a>
        </div>
      </div>
    </nav>
  );
}