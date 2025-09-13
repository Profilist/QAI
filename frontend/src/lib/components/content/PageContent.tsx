import Breadcrumbs from "./utilities/Breadcrumbs";
import Hr from "./utilities/Hr";
import PageTitle from "./utilities/PageTitle";

export default function PageContent({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full">
      {/* Breadcrumb */}
      <Breadcrumbs />

      <section className="flex flex-col gap-6 px-9 h-full">
        {/* Page title */}
        <div className="pt-8">
          <PageTitle title={title} />
        </div>
        <Hr />
        {children}
      </section>
    </div>
  );
}
