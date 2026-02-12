import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">
          Stock<span className="text-blue-600">Buddy</span>
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          AI-powered stock portfolio analysis and earnings insights
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            href="/sign-up"
            className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
          <Link
            href="/sign-in"
            className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
