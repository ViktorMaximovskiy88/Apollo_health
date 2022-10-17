import { CommentWall } from '../comments/CommentWall';
import { DocDocument } from './types';

export function DocDocumentCommentsTab({ doc }: { doc: DocDocument }) {
  return <CommentWall targetId={doc._id} />;
}
