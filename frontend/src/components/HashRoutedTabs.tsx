import { TabsProps, Tabs } from 'antd';
import { useState, useCallback, useEffect } from 'react';

export function HashRoutedTabs(props: TabsProps) {
  const defaultTab = props.defaultActiveKey || props.items?.[0].key;
  const [activeTab, setActiveTab] = useState(window.location.hash.replace('#', '') || defaultTab);
  const onTabClick = useCallback(
    (key: string) => {
      setActiveTab(key);
    },
    [setActiveTab]
  );

  useEffect(() => {
    window.history.replaceState(null, '', `#${activeTab}`);
  }, [activeTab]);

  return <Tabs onTabClick={onTabClick} activeKey={activeTab} {...props} />;
}
