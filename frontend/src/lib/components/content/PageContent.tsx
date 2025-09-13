import Breadcrumbs from "./utilities/Breadcrumbs";
import Hr from "./utilities/Hr";
import PageTitle from "./utilities/PageTitle";

export default function PageContent({
  title,
  breadcrumb,
  children,
}: {
  title: string;
  breadcrumb: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full">
      {/* Breadcrumb */}
      <Breadcrumbs breadcrumb={breadcrumb} />

      <section className="flex flex-col gap-6 px-9 h-full">
        {/* Page title */}
        <PageTitle title={title} />
        <Hr />
        {children}
      </section>
    </div>
  );
}
