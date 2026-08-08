import { ProductEditor } from "@/features/products/ProductEditor";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ProductDetailPage({ params }: Props) {
  const { id } = await params;
  return <ProductEditor productId={id} />;
}
