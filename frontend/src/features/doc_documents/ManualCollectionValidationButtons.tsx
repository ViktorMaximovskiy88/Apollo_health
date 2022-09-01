import { Button } from 'antd';
import {
  FileAddOutlined,
  FileDoneOutlined,
  FileExcelOutlined,
  FileExclamationOutlined,
  FileUnknownOutlined,
} from '@ant-design/icons';
import { DocDocument } from './types';
import { useState } from 'react';

const FoundSelected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button type="primary" name="found" onClick={() => handleClick('found')}>
    <FileDoneOutlined className="text-white" />
  </Button>
);
const FoundUnselected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button name="found" onClick={() => handleClick('found')}>
    <FileDoneOutlined />
  </Button>
);

const NewDocSelected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button type="primary" name="newDoc" onClick={() => handleClick('newDoc')}>
    <FileAddOutlined className="text-white" />
  </Button>
);
const NewDocUnselected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button name="newDoc" onClick={() => handleClick('newDoc')}>
    <FileAddOutlined />
  </Button>
);

const NotFoundSelected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button type="primary" name="notFound" onClick={() => handleClick('notFound')}>
    <FileExcelOutlined className="text-white" />
  </Button>
);
const NotFoundUnselected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button name="notFound" onClick={() => handleClick('notFound')}>
    <FileExcelOutlined />
  </Button>
);

const UnhandledSelected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button type="primary" name="unhandled" onClick={() => handleClick('unhandled')}>
    <FileUnknownOutlined className="text-white" />
  </Button>
);
const UnhandledUnselected = ({ handleClick }: { handleClick: (button: string) => void }) => (
  <Button name="unhandled" onClick={() => handleClick('unhandled')}>
    <FileUnknownOutlined />
  </Button>
);

export const NewVersion = ({
  doc,
  handleNewVersion,
}: {
  doc: DocDocument;
  handleNewVersion: (doc: DocDocument) => void;
}) => (
  <Button>
    <FileExclamationOutlined onClick={() => handleNewVersion(doc)} />
  </Button>
);

export function ValidationButtons({
  doc,
  handleNewVersion,
}: {
  doc: DocDocument;
  handleNewVersion: (doc: DocDocument) => void;
}) {
  const [found, setFound] = useState(false);
  const [newDoc, setNewDoc] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [unhandled, setUnhandled] = useState(true);

  const handleClick = (button: string) => {
    switch (button) {
      case 'found':
        return setFound(!found);
      case 'newDoc':
        return setNewDoc(!newDoc);
      case 'notFound':
        return setNotFound(!notFound);
      case 'unhandled':
        setUnhandled(!unhandled);
    }
  };

  return (
    <div className="flex space-x-1">
      {found ? (
        <FoundSelected handleClick={handleClick} />
      ) : (
        <FoundUnselected handleClick={handleClick} />
      )}
      {newDoc ? (
        <NewDocSelected handleClick={handleClick} />
      ) : (
        <NewDocUnselected handleClick={handleClick} />
      )}
      {notFound ? (
        <NotFoundSelected handleClick={handleClick} />
      ) : (
        <NotFoundUnselected handleClick={handleClick} />
      )}
      <NewVersion doc={doc} handleNewVersion={handleNewVersion} />
      {unhandled ? (
        <UnhandledSelected handleClick={handleClick} />
      ) : (
        <UnhandledUnselected handleClick={handleClick} />
      )}
    </div>
  );
}
