import Layout from "antd/lib/layout/layout";
import Title from "antd/lib/typography/Title";
import { useParams } from "react-router-dom";
import { useGetDocDocumentQuery } from "./docDocumentApi";

export function DocDocumentEditPage() {
    const docId = useParams().docDocumentId
    const { data: doc } = useGetDocDocumentQuery(docId);
    if (!doc) return null;

    return (
        <Layout className="p-4 bg-transparent">
            <Title level={4}>
              {doc.name}
            </Title>
        </Layout>
    )
}