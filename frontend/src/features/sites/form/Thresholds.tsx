import { Form, Slider } from 'antd';

const formatter = (value?: number) => {
  if (!value) return;
  const displayedValue = Math.round(value * 100); // fix floating point math bugs
  return `${displayedValue}%`;
};

export function DocumentTypeThreshold() {
  return (
    <Form.Item name="doc_type_threshold" label="Document Type Threshold">
      <Slider
        min={0}
        max={1}
        step={0.01}
        tipFormatter={formatter}
        tooltip={{
          open: true,
          getPopupContainer: (triggerNode) => triggerNode.parentElement ?? triggerNode, // fixes tooltip to be inline with element -- https://github.com/ant-design/ant-design/issues/25117#issuecomment-873747921
        }}
      />
    </Form.Item>
  );
}

export function LineageThreshold() {
  return (
    <Form.Item name="lineage_threshold" label="Lineage Threshold">
      <Slider
        min={0}
        max={1}
        step={0.01}
        tipFormatter={formatter}
        tooltip={{
          open: true,
          getPopupContainer: (triggerNode) => triggerNode.parentElement ?? triggerNode, // fixes tooltip to be inline with element -- https://github.com/ant-design/ant-design/issues/25117#issuecomment-873747921
        }}
      />
    </Form.Item>
  );
}
