import { Layout, Button, Table } from "antd";
import Title from "antd/lib/typography/Title";
import { Link, useParams } from "react-router-dom";
import { ButtonLink } from "../../components/ButtonLink";
import { useGetWorkQueueAssessmentsQuery } from "../assessments/assessmentsApi";
import { DocumentAssessment } from "../assessments/types";
import { useGetWorkQueueQuery } from "./workQueuesApi";

export function WorkQueuePage() {
    const queueId = useParams().queueId;
    const { data: assessments } = useGetWorkQueueAssessmentsQuery(queueId);
    const { data: wq } = useGetWorkQueueQuery(queueId);
    if (!wq) return null;

    const columns = [
        {
            title: "Name",
            key: "name",
            render: (assessment: DocumentAssessment) => {
                return <ButtonLink to={`${assessment._id}/read-only`}>
                    {assessment.name}
                </ButtonLink>
            }
        },
        {
            title: "Actions",
            render: (assessment: DocumentAssessment) => {
                return <ButtonLink type='default' to={`${assessment._id}/process`}>
                    Take
                </ButtonLink>
            }
        },
    ]
    return (
        <Layout className="bg-transparent p-4">
          <div className="flex">
            <Title className="inline-block" level={4}>
              {wq.name}
            </Title>
            <Link className="ml-auto" to="take-next">
              <Button>Take Next</Button>
            </Link>
          </div>
          <Table dataSource={assessments} columns={columns} pagination={{ pageSize: 50 }}/>
        </Layout>
    );
}