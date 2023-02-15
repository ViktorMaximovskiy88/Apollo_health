import { Button, Checkbox, Empty, Pagination, Popover, Radio, RadioChangeEvent } from 'antd';
import {
  CompassOutlined,
  LeftOutlined,
  MinusCircleFilled,
  PlusCircleFilled,
  RightCircleOutlined,
  RightOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { Dispatch, SetStateAction, useCallback, useMemo, useState } from 'react';

import { DocumentSection, TagComparison, TagType } from '../types';
import { Hr } from '../../../components';
import { CheckboxChangeEvent } from 'antd/lib/checkbox';

function PaginationControl({
  goToPage,
  maxPage,
  currentPage,
}: {
  goToPage: (page: number) => void;
  maxPage: undefined | number;
  currentPage: number;
}) {
  let totalPages = maxPage ? maxPage : 1;
  const current = currentPage + 1;
  return (
    <div className="flex flex-col items-center">
      Go to Page
      <Pagination
        current={current}
        defaultCurrent={1}
        disabled={!maxPage}
        onChange={goToPage}
        pageSize={1}
        simple
        total={totalPages}
      />
    </div>
  );
}

function SectionItem({
  sectionData,
  symbol,
  statusText,
  selectSection,
}: {
  sectionData: { section: DocumentSection; key: number };
  symbol?: JSX.Element;
  statusText?: string;
  selectSection: (id: number) => void;
}) {
  const { section, key } = sectionData;
  return (
    <div className="mx-2">
      <div className="grid grid-cols-10 truncate items-center">
        {symbol}
        <div className="col-span-2 font-black">{statusText}</div>
        <div className="col-span-6 truncate mr-1 max-w-xs">{section.key_text}</div>
        <Button className="px-2" shape="circle" type="text" onClick={(e) => selectSection(key)}>
          <RightCircleOutlined />
        </Button>
      </div>
      <Hr className="bg-zinc-300 my-1 h-[1px]" />
    </div>
  );
}

function SectionNavigator({
  currentSectionType,
  goToSection,
  setCurrentSectionType,
  setCurrentDocSection,
  toggleOnlyChanges,
  currentSections,
}: {
  currentSectionType: TagType;
  goToSection: (sectionId: number, sectionType: TagType) => void;
  setCurrentSectionType: Dispatch<SetStateAction<TagType>>;
  setCurrentDocSection: Dispatch<SetStateAction<number | undefined>>;
  toggleOnlyChanges: (e: CheckboxChangeEvent) => void;
  currentSections: {
    section: DocumentSection;
    key: number;
  }[];
}) {
  const handleSectionTypeChange = (e: RadioChangeEvent) => {
    setCurrentSectionType(e.target.value);
    setCurrentDocSection(undefined);
  };

  const handleSectionClick = (id: number) => {
    goToSection(id, currentSectionType);
  };

  const symbols = {
    ADDED: <PlusCircleFilled className="text-green-600" />,
    REMOVED: <MinusCircleFilled className="text-red-500" />,
    CHANGED: <PlusCircleFilled className="text-orange-300" />,
    UNCHANGED: <MinusCircleFilled className="text-zinc-600" />,
  };
  const statusTexts = {
    ADDED: 'Added',
    REMOVED: 'Removed',
    CHANGED: 'Changed',
  };

  return (
    <div className="h-80" style={{ minWidth: '28rem' }}>
      <div className="flex items-center justify-between mx-5 font-bold">
        <span className="mx-3">Sections</span>
        <Radio.Group defaultValue="therapy" onChange={handleSectionTypeChange}>
          <Radio.Button value="therapy">Therapies</Radio.Button>
          <Radio.Button value="indication">Indications</Radio.Button>
        </Radio.Group>
        <div>
          <label htmlFor="only-changes" className="mx-2">
            Only Changes
          </label>
          <Checkbox id="only-changes" onChange={toggleOnlyChanges} />
        </div>
      </div>
      <Hr className="bg-zinc-400 my-2 mx-3 h-[1px]" />
      {currentSections.length > 0 ? (
        <ul className="max-h-64 overflow-scroll" style={{ paddingInlineStart: 0 }}>
          {currentSections.map((sectionData) => {
            const status = sectionData.section.section_status;
            const symbol = status ? symbols[status] : symbols.UNCHANGED;
            const statusText = status ? statusTexts[status] : 'No Change';
            return (
              <SectionItem
                key={sectionData.key}
                selectSection={handleSectionClick}
                sectionData={sectionData}
                symbol={symbol}
                statusText={statusText}
              />
            );
          })}
        </ul>
      ) : (
        <Empty className="my-10" />
      )}
    </div>
  );
}

function SectionNavigation({
  tagComparison,
  currentDocSection,
  setCurrentDocSection,
  updateCurrentPdfPage,
  updatePreviousPdfPage,
}: {
  currentDocSection?: number;
  setCurrentDocSection: Dispatch<SetStateAction<number | undefined>>;
  tagComparison?: TagComparison;
  updateCurrentPdfPage: (page: number) => void;
  updatePreviousPdfPage: (page: number) => void;
}) {
  const [currentSectionType, setCurrentSectionType] = useState<TagType>(TagType.Therapy);
  const [onlyChanges, setOnlyChanges] = useState(false);

  const toggleOnlyChanges = (e: CheckboxChangeEvent) => {
    setOnlyChanges(e.target.checked);
  };

  const currentSections = useMemo(() => {
    if (!tagComparison) {
      return [];
    }
    const sectionsByType =
      currentSectionType === TagType.Therapy
        ? tagComparison.therapy_tag_sections
        : tagComparison.indication_tag_sections;

    let finalSections = sectionsByType.map((section, i) => {
      return { section, key: i };
    });
    if (onlyChanges) {
      finalSections = finalSections.filter((sectionData) => sectionData.section.section_status);
    }
    return finalSections;
  }, [currentSectionType, onlyChanges, tagComparison]);

  const goToSection = useCallback(
    (sectionId: number, sectionType: TagType) => {
      if (!tagComparison) {
        return;
      }
      const newSection =
        sectionType === TagType.Therapy
          ? tagComparison?.therapy_tag_sections[sectionId]
          : tagComparison?.indication_tag_sections[sectionId];

      if (newSection.current_page != null && newSection.prev_page != null) {
        updateCurrentPdfPage(newSection.current_page);
        updatePreviousPdfPage(newSection.prev_page);
      } else if (newSection.current_page != null) {
        updateCurrentPdfPage(newSection.current_page);
        updatePreviousPdfPage(newSection.current_page);
      } else if (newSection.prev_page != null) {
        updateCurrentPdfPage(newSection.prev_page);
        updatePreviousPdfPage(newSection.prev_page);
      }
      setCurrentDocSection(sectionId);
    },
    [setCurrentDocSection, tagComparison, updateCurrentPdfPage, updatePreviousPdfPage]
  );

  const incrementSection = (change: number) => {
    if (currentDocSection === undefined || tagComparison === undefined) {
      return;
    }
    const currentSectionData = currentSections.findIndex(
      (sectionsData) => sectionsData.key === currentDocSection
    );
    const newSectionId = currentSections[currentSectionData + change].key;
    goToSection(newSectionId, currentSectionType);
  };

  const disablePrevious = useMemo(() => {
    if (onlyChanges) {
      const currentSectionData = currentSections.findIndex(
        (sectionsData) => sectionsData.key === currentDocSection
      );
      return currentSectionData <= 0;
    }
    return !currentDocSection || tagComparison === undefined;
  }, [onlyChanges, currentSections, currentDocSection, tagComparison]);

  const disableNext = useMemo(() => {
    if (onlyChanges) {
      const currentSectionData = currentSections.findIndex(
        (sectionsData) => sectionsData.key === currentDocSection
      );
      return currentSectionData >= currentSections.length - 1 || currentSectionData === -1;
    }
    if (currentDocSection === undefined || tagComparison === undefined) {
      return true;
    }
    if (currentSectionType === TagType.Therapy) {
      return tagComparison?.therapy_tag_sections.length - 1 <= currentDocSection;
    }
    if (currentSectionType === TagType.Indication) {
      return tagComparison?.indication_tag_sections.length - 1 <= currentDocSection;
    }
    return false;
  }, [onlyChanges, currentDocSection, currentSectionType, currentSections, tagComparison]);

  return (
    <div className="flex">
      <div className="flex mx-5">
        <Button onClick={(e) => incrementSection(-1)} disabled={disablePrevious} type="link">
          <LeftOutlined /> Go to Previous Section
        </Button>
        <Button onClick={(e) => incrementSection(1)} disabled={disableNext} type="link">
          Go to Next Section <RightOutlined />
        </Button>
      </div>
      {tagComparison ? (
        <Popover
          trigger="click"
          content={
            <SectionNavigator
              goToSection={goToSection}
              currentSectionType={currentSectionType}
              setCurrentSectionType={setCurrentSectionType}
              setCurrentDocSection={setCurrentDocSection}
              toggleOnlyChanges={toggleOnlyChanges}
              currentSections={currentSections}
            />
          }
        >
          <Button className="max-h-8" icon={<CompassOutlined />}>
            Section Navigator
          </Button>
        </Popover>
      ) : (
        <Button disabled icon={<CompassOutlined />}>
          Section Navigator
        </Button>
      )}
    </div>
  );
}

export function CompareModalFooter({
  tagComparison,
  updateCurrentPdfPage,
  updatePreviousPdfPage,
  hasDocPages,
  maxPage,
  latestPage,
  processCompare,
}: {
  tagComparison?: TagComparison;
  updateCurrentPdfPage: (page: number) => void;
  updatePreviousPdfPage: (page: number) => void;
  hasDocPages: boolean;
  maxPage?: number;
  latestPage: number;
  processCompare?: () => void;
}) {
  const [currentDocSection, setCurrentDocSection] = useState<number>();

  const goToPage = (page: number) => {
    setCurrentDocSection(undefined);
    updateCurrentPdfPage(page - 1);
    updatePreviousPdfPage(page - 1);
  };

  return (
    <>
      {hasDocPages ? (
        <div className="flex items-center">
          <PaginationControl maxPage={maxPage} goToPage={goToPage} currentPage={latestPage} />
          <SectionNavigation
            tagComparison={tagComparison}
            currentDocSection={currentDocSection}
            setCurrentDocSection={setCurrentDocSection}
            updateCurrentPdfPage={updateCurrentPdfPage}
            updatePreviousPdfPage={updatePreviousPdfPage}
          />
          {processCompare ? (
            <Button className="ml-auto mr-2" onClick={processCompare} icon={<ReloadOutlined />}>
              Reprocess
            </Button>
          ) : (
            <></>
          )}
        </div>
      ) : (
        <></>
      )}
    </>
  );
}
