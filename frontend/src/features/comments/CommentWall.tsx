import { Avatar, Button, Comment as CommentComponent, Form, Input } from 'antd';
import { ReactNode, useCallback, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { prettyDateTimeFromISO } from '../../common';
import { useCurrentUser } from '../../common/hooks/use-current-user';
import { User } from '../users/types';
import { useGetUserQuery } from '../users/usersApi';
import {
  useAddCommentMutation,
  useDeleteCommentMutation,
  useGetCommentsQuery,
} from './commentsApi';
import { Comment } from './types';
import remarkGfm from 'remark-gfm';

const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];

export function UserAvatar({ user }: { user?: User }) {
  const firstLetter = user?.full_name[0];
  const simpleHash =
    user?.full_name
      .split('')
      .map((c) => c.charCodeAt(0))
      .reduce((a, b) => a + b) || 0;
  const color = colors[simpleHash % colors.length];
  return <Avatar style={{ backgroundColor: color }}>{firstLetter}</Avatar>;
}

export function AuthoredComment({ comment }: { comment: Comment }) {
  const { data: author } = useGetUserQuery(comment.user_id);
  const user = useCurrentUser();

  const [onDeleteMutation] = useDeleteCommentMutation();
  const onDelete = useCallback(async () => {
    await onDeleteMutation(comment);
  }, [onDeleteMutation]);
  const actions: ReactNode[] = [];
  if (author?._id === user?._id) {
    actions.push(
      <span key="delete" onClick={onDelete}>
        Delete
      </span>
    );
  }

  return (
    <CommentComponent
      avatar={<UserAvatar user={author} />}
      datetime={prettyDateTimeFromISO(comment.time)}
      author={author?.full_name}
      content={<ReactMarkdown remarkPlugins={[remarkGfm]}>{comment.text}</ReactMarkdown>}
      actions={actions}
    />
  );
}

export function NewComment({ targetId }: { targetId: string }) {
  const [addComment] = useAddCommentMutation();
  const [text, setText] = useState('');
  const onFinish = useCallback(() => {
    setText('');
    addComment({
      target_id: targetId,
      text,
    });
  }, [addComment, text, targetId]);
  return (
    <div>
      <Form.Item>
        <Input.TextArea onChange={(t) => setText(t.target.value)} value={text} />
      </Form.Item>
      <Form.Item>
        <Button type="primary" onClick={onFinish}>
          Add Note
        </Button>
      </Form.Item>
    </div>
  );
}

export function CommentWall({ targetId }: { targetId: string }) {
  const { data: comments } = useGetCommentsQuery(targetId, { refetchOnMountOrArgChange: true });
  return (
    <div>
      {comments?.data.map((comment) => {
        return <AuthoredComment comment={comment} />;
      })}
      <NewComment targetId={targetId} />
    </div>
  );
}
