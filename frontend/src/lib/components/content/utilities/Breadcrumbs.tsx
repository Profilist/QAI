export default function Breadcrumbs({ breadcrumb }: { breadcrumb: string }) {
    return (
        <section className="px-9 py-6">
            <p>{breadcrumb}</p>
        </section>
    )
}
