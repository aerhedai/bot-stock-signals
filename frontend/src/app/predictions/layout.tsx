import TabBar from "@/components/layout/TabBar";

const tabs = [
  { href: "/predictions/stocks", label: "Stocks" },
  { href: "/predictions/crypto", label: "Crypto" },
];

export default function PredictionsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <TabBar tabs={tabs} />
      {children}
    </div>
  );
}
