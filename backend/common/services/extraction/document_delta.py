from backend.common.models.doc_document import DocDocument
from backend.common.models.shared import TherapyTag


class DocumentDeltaCreator:
    def tags_by_section(self, tags: list[TherapyTag]) -> dict[str, list[TherapyTag]]:
        by_section: dict[str, list[TherapyTag]] = {}
        for tag in tags:
            if tag.removed:
                continue

            section = tag.section
            by_section.setdefault(section, [])
            by_section[section].append(tag)
        return by_section

    def tags_by_focus(
        self, tags_by_section: dict[str, list[TherapyTag]]
    ) -> dict[set[str], list[TherapyTag]]:
        by_section: dict[set[str], list[TherapyTag]] = {}
        for tags in tags_by_section.values():
            focus_tags: set[str] = set()
            for tag in tags:
                if tag.focus:
                    focus_tags.add(tag.code)
            by_section[focus_tags] = tags
        return by_section

    def create_delta(self, new_doc: DocDocument, old_doc: DocDocument) -> DocDocument:
        new_tags_by_section = self.tags_by_section(new_doc.therapy_tags)
        old_tags_by_section = self.tags_by_section(old_doc.therapy_tags)
        old_tags_by_focus = self.tags_by_focus(old_tags_by_section)
        for section, tags in new_tags_by_section.items():
            # Perfect match, no change
            if section in old_tags_by_section:
                del old_tags_by_section[section]
                continue

            focus_tags: set[str] = set()
            for tag in tags:
                if tag.focus:
                    focus_tags.add(tag.code)

            old_tags = old_tags_by_focus.pop(focus_tags, None)
            # Same focus, new text, list as edit
            if old_tags:
                for tag in tags:
                    tag.edit = True
                continue

            # Entirely new focus
            for tag in tags:
                tag.add = True

        new_tags = []
        for tags in new_tags_by_section.values():
            for tag in tags:
                new_tags.append(tag)

        # remaining old tags are the ones that where removed
        for tags in old_tags_by_focus.values():
            for tag in tags:
                tag.add = False
                tag.edit = False
                tag.removed = True
                new_tags.append(tag)

        new_tags.sort(key=lambda tag: tag.page)
        new_doc.therapy_tags = new_tags

        return new_doc
