export default {
  props: ["options"],
  template: `
    <q-select
      ref="qRef"
      v-bind="$attrs"
      :options="displayedOptions"
      @popup-show="onPopupShow"
      @popup-hide="onPopupHide"
    >
      <template v-slot:before-options>
        <div class="search-select-header q-px-sm q-pt-sm q-pb-xs" style="position: sticky; top: 0; z-index: 100;">
          <q-input
            ref="searchInputRef"
            v-model="searchQuery"
            dense
            outlined
            placeholder="Search..."
            @click.stop
            @keydown.stop
            clearable
            autofocus
            style="font-size: 13px;"
          >
            <template v-slot:prepend>
              <q-icon name="search" size="18px" color="grey-6" />
            </template>
          </q-input>
        </div>
      </template>
      <template v-slot:no-option>
        <div class="search-select-header q-px-sm q-pt-sm q-pb-xs" style="position: sticky; top: 0; z-index: 100;">
          <q-input
            ref="searchInputRef"
            v-model="searchQuery"
            dense
            outlined
            placeholder="Search..."
            @click.stop
            @keydown.stop
            clearable
            autofocus
            style="font-size: 13px;"
          >
            <template v-slot:prepend>
              <q-icon name="search" size="18px" color="grey-6" />
            </template>
          </q-input>
        </div>
        <q-item>
          <q-item-section class="text-grey text-center" style="font-size: 12.5px; padding: 12px 0;">
            No matching options
          </q-item-section>
        </q-item>
      </template>
      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">
        <slot :name="slot" v-bind="slotProps || {}" />
      </template>
    </q-select>
  `,
  data() {
    return {
      searchQuery: "",
    };
  },
  computed: {
    displayedOptions() {
      if (!this.searchQuery || !this.searchQuery.trim()) {
        return this.options || [];
      }
      const q = this.searchQuery.toLowerCase().trim();
      return (this.options || []).filter((opt) => {
        const label = typeof opt === "object" && opt !== null ? String(opt.label ?? opt.value ?? "") : String(opt);
        return label.toLowerCase().includes(q);
      });
    },
  },
  methods: {
    onPopupShow() {
      this.$nextTick(() => {
        if (this.$refs.searchInputRef) {
          this.$refs.searchInputRef.focus();
        }
      });
    },
    onPopupHide() {
      this.searchQuery = "";
    },
  },
};
