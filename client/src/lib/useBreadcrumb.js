/**
 * lib/useBreadcrumb.js
 * Tiny hook a page calls once to register its breadcrumb trail with the
 * shared uiSlice, e.g. useBreadcrumb([{ label: "My Trips", path: "/trips" }]).
 */
import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { setBreadcrumbs } from "../store/slices/uiSlice";

export function useBreadcrumb(crumbs) {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(setBreadcrumbs(crumbs));
    return () => dispatch(setBreadcrumbs([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(crumbs)]);
}
